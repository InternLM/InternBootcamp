import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cjzzhuandapples.Cjzzhuandapples_reward_calculator import CjzzhuandapplesRewardCalculator

# 导入依赖库
import math
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CjzzhuandapplesVerificationTool(BaseTool):
    """Cjzzhuandapples验证工具"""
    
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
            score = CjzzhuandapplesRewardCalculator.verify_score(
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
            logger.error(f"CjzzhuandapplesVerificationTool执行错误: {str(e)}")
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
    def compute_max_groups(n):
        if n < 2:
            return 0
        used = [False] * (n + 1)
        primes = []

        # Efficient sieve to find primes up to n//2
        sieve_size = (n // 2) + 1
        sieve = [True] * sieve_size
        sieve[0] = sieve[1] = False
        for i in range(2, int(math.isqrt(sieve_size)) + 1):
            if sieve[i]:
                sieve[i*i::i] = [False] * len(sieve[i*i::i])

        # Collect primes in the order: odd primes first, then 2
        primes = [i for i in range(3, sieve_size, 2) if sieve[i]]
        if 2 <= sieve_size:
            primes.append(2)

        total_groups = 0
        for prime in primes:
            if prime > n // 2:
                continue

            # Collect multiples of prime
            multiples = []
            if not used[prime]:
                multiples.append(prime)
                used[prime] = True

            max_multiple = n // prime
            for multiplier in range(3, max_multiple + 1):
                num = prime * multiplier
                if not used[num]:
                    multiples.append(num)
                    used[num] = True

            # Handle odd count
            if len(multiples) % 2 != 0:
                candidate = prime * 2
                if candidate <= n and not used[candidate]:
                    multiples.append(candidate)
                    used[candidate] = True

            total_groups += len(multiples) // 2

        return total_groups
