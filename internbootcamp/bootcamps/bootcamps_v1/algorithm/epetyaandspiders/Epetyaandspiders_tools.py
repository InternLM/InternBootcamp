import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.epetyaandspiders.Epetyaandspiders_reward_calculator import EpetyaandspidersRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def get_bit(a, n):
    return (a >> n) & 1

def reset_bit(a, n):
    return a & ~(1 << n)

def calculate_max_empty(n, m):
    # Ensure n is the larger dimension for optimization
    if m > n:
        n, m = m, n
    if m == 0:
        return 0  # Should not happen for valid input
    max_size = 1 << m
    dp = [[[-1000] * max_size for _ in range(max_size)] for __ in range(n + 1)]
    initial_mask = (1 << m) - 1
    dp[0][0][initial_mask] = 0
    
    for i in range(1, n + 1):
        for prev_row in range(max_size):
            for prev_mask in range(max_size):
                if dp[i-1][prev_row][prev_mask] == -1000:
                    continue
                for current_row in range(max_size):
                    # Calculate spiders present in current configuration
                    combined = prev_row | current_row
                    cnt = sum(1 for bit in range(m) if not get_bit(combined, bit))
                    
                    # Calculate new_mask based on spider movements
                    new_mask = initial_mask
                    for bit in range(m):
                        if get_bit(combined, bit):
                            if m == 1:
                                new_mask = reset_bit(new_mask, 0)
                            else:
                                for offset in (-1, 0, 1):
                                    pos = bit + offset
                                    if 0 <= pos < m:
                                        new_mask = reset_bit(new_mask, pos)
                    
                    next_mask = new_mask & prev_mask
                    dp[i][next_mask][current_row] = max(
                        dp[i][next_mask][current_row], 
                        dp[i-1][prev_row][prev_mask] + cnt
                    )
    
    # Find maximum value in final state
    return max(dp[n][0][state] for state in range(max_size))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EpetyaandspidersVerificationTool(BaseTool):
    """Epetyaandspiders验证工具"""
    
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
            score = EpetyaandspidersRewardCalculator.verify_score(
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
            logger.error(f"EpetyaandspidersVerificationTool执行错误: {str(e)}")
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

