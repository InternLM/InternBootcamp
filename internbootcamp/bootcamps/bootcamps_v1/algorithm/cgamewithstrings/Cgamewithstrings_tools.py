import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cgamewithstrings.Cgamewithstrings_reward_calculator import CgamewithstringsRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CgamewithstringsVerificationTool(BaseTool):
    """Cgamewithstrings验证工具"""
    
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
            score = CgamewithstringsRewardCalculator.verify_score(
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
            logger.error(f"CgamewithstringsVerificationTool执行错误: {str(e)}")
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
    @staticmethod
    def calculate_expected_value(strings):
        n = len(strings)
        if n == 0:
            return 0.0
        m = len(strings[0])
        if any(len(s) != m for s in strings):
            raise ValueError("All strings must have the same length")

        w = [0] * (1 << m)
        for i in range(n):
            for j in range(i):
                mask = 0
                for k in range(m):
                    if strings[i][k] == strings[j][k]:
                        mask |= 1 << k
                w[mask] |= (1 << i) | (1 << j)

        # Propagate the masks
        for mask in reversed(range(1 << m)):
            for k in range(m):
                if mask & (1 << k):
                    lower_mask = mask ^ (1 << k)
                    w[lower_mask] |= w[mask]

        cnt = [0] * (1 << m)
        for mask in range(1 << m):
            cnt[mask] = bin(w[mask]).count('1')

        dp = [0.0] * (1 << m)
        for mask in reversed(range(1 << m)):
            if cnt[mask] == 0:
                continue
            asked = bin(mask).count('1')
            remaining = m - asked
            if remaining == 0:
                dp[mask] = 0.0
                continue
            total = 0.0
            for k in range(m):
                if not (mask & (1 << k)):
                    next_mask = mask | (1 << k)
                    total += dp[next_mask] * cnt[next_mask]
            dp[mask] = 1 + total / (remaining * cnt[mask])
        return dp[0]
