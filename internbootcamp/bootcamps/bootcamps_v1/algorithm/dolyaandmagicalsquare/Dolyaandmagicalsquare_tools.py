import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dolyaandmagicalsquare.Dolyaandmagicalsquare_reward_calculator import DolyaandmagicalsquareRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def solve_case(n_input, k_input):
    MAX_PRECOMPUTE = 100
    f = [0]
    for _ in range(MAX_PRECOMPUTE):
        f.append(f[-1] * 4 + 1)
    p = [0]
    for g in range(MAX_PRECOMPUTE):
        p.append(p[-1] + (2 ** (g + 1) - 1))
    
    n, k = n_input, k_input

    if k == 1:
        return f"YES {n-1}"
    
    # 计算最大可能的分割次数（不考虑路径条件）
    max_f = (4**n - 1) // 3
    if k > max_f:
        return "NO"
    
    original_n = n
    
    # 直接遍历所有可能的j（不截断n）
    for j in range(original_n - 1, -1, -1):
        m_segment = original_n - j
        
        # 计算当前段的p值
        if m_segment < len(p):
            current_p = p[m_segment]
        else:
            current_p = 2 * (2**m_segment - 1) - m_segment
        
        if current_p > k:
            continue
        
        # 计算剩余可用分割次数
        other = 2 ** m_segment
        if j < len(f):
            f_j = f[j]
        else:
            f_j = (4**j - 1) // 3
        
        avail = (other - 1) ** 2 * f_j
        
        # 判断是否满足总分割次数
        if current_p + avail >= k:
            answer_m = original_n - m_segment
            return f"YES {answer_m}"
    
    return "NO"

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DolyaandmagicalsquareVerificationTool(BaseTool):
    """Dolyaandmagicalsquare验证工具"""
    
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
            score = DolyaandmagicalsquareRewardCalculator.verify_score(
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
            logger.error(f"DolyaandmagicalsquareVerificationTool执行错误: {str(e)}")
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

