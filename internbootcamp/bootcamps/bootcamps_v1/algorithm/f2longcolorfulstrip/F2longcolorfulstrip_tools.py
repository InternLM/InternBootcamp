import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.f2longcolorfulstrip.F2longcolorfulstrip_reward_calculator import F2longcolorfulstripRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 998244353



# === 源文件中的全局函数 ===

def compute_answer(n_input, m_input, c_list):
    # Correctly map problem's n (number of colors) and m (strip length) to reference code's variables
    m_code = n_input  # Reference code's m represents problem's n (number of colors)
    n_code = m_input  # Reference code's n represents problem's m (strip length)

    C = [x - 1 for x in c_list]
    
    # Compress consecutive duplicates
    if not C:
        return 0
    C2 = [C[0]]
    for c in C[1:]:
        if C2[-1] != c:
            C2.append(c)
    new_n = len(C2)
    
    # Check if compressed length exceeds 2*m_code (problem's n)
    if new_n > 2 * m_code:
        return 0
    
    pos = [[] for _ in range(m_code)]
    for i in range(new_n):
        c = C2[i]
        if c >= m_code or c < 0:
            return 0
        pos[c].append(i)
    
    # Verify all colors are present
    for color in range(m_code):
        if not pos[color]:
            return 0
    
    DP = [[1] * (new_n + 1) for _ in range(new_n + 1)]
    
    for le in range(1, new_n + 1):
        for i in range(new_n - le + 1):
            j = i + le
            min_color = min(C2[i:j])
            min_indices = [p for p in range(i, j) if C2[p] == min_color]
            if not min_indices:
                DP[i][j] = 0
                continue
            
            first = min(min_indices)
            last = max(min_indices)
            
            # Calculate left part
            left = 0
            for k in range(i, first + 1):
                left = (left + DP[i][k] * DP[k][first]) % MOD
            
            # Calculate right part
            right = 0
            for k in range(last + 1, j + 1):
                right = (right + DP[last + 1][k] * DP[k][j]) % MOD
            
            # Calculate middle parts between occurrences of min_color
            middle = 1
            color_positions = pos[min_color]
            for idx in range(len(color_positions) - 1):
                prev = color_positions[idx]
                next_p = color_positions[idx + 1]
                if prev < i or next_p >= j:
                    continue
                middle = (middle * DP[prev + 1][next_p]) % MOD
            
            DP[i][j] = (left * right % MOD) * middle % MOD
    
    return DP[0][new_n]

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class F2longcolorfulstripVerificationTool(BaseTool):
    """F2longcolorfulstrip验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = F2longcolorfulstripRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"F2longcolorfulstripVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
    # 其他额外方法

