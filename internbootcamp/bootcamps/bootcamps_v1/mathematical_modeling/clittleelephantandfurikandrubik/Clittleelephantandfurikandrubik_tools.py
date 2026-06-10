import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.clittleelephantandfurikandrubik.Clittleelephantandfurikandrubik_reward_calculator import ClittleelephantandfurikandrubikRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_expected(n, a_str, b_str):
    a = [[[] for _ in range(26)] for __ in range(2)]
    for i, s in enumerate([a_str, b_str]):
        for j, c in enumerate(s):
            idx = ord(c) - ord('A')
            a[i][idx].append(j)
    
    total = 0
    for char_idx in range(26):
        p = a[0][char_idx]
        q = a[1][char_idx]
        if not p or not q:
            continue
        
        q_sum = sum(q)
        p_len = len(p)
        q_len = len(q)
        j = 0
        t = 0
        
        for x in p:
            # 维护双指针找到q中第一个不小于x的位置
            while j < q_len and q[j] < x:
                t += q[j]
                j += 1
            
            # 计算两项贡献（参考原算法逻辑）
            part1 = (t + j * x) * (n - x)
            part2 = (x + 1) * (n * (q_len - j) - (q_sum - t))
            total += part1 + part2
    
    # 计算分母：n*(n+1)*(2n+1)/6
    denominator = n * (n + 1) * (2 * n + 1) / 6
    if denominator == 0:
        return 0.0
    return total * 6.0 / (n * (n + 1) * (2 * n + 1))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ClittleelephantandfurikandrubikVerificationTool(BaseTool):
    """Clittleelephantandfurikandrubik验证工具"""
    
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
            score = ClittleelephantandfurikandrubikRewardCalculator.verify_score(
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
            logger.error(f"ClittleelephantandfurikandrubikVerificationTool执行错误: {str(e)}")
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

