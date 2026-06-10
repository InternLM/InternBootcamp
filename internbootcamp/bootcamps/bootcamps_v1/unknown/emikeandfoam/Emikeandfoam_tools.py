import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.unknown.emikeandfoam.Emikeandfoam_reward_calculator import EmikeandfoamRewardCalculator

# 导入依赖库
import math
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EmikeandfoamVerificationTool(BaseTool):
    """Emikeandfoam验证工具"""
    
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
            score = EmikeandfoamRewardCalculator.verify_score(
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
            logger.error(f"EmikeandfoamVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def _compute_expected(cls, n, q, a, queries):
        # 预计算每个数的质因数分解
        prime_factors_list = []
        max_ai = max(a) if a else 1
        sieve = cls._build_sieve(max_ai)

        for num in a:
            factors = set()
            temp = num
            while temp > 1:
                p = sieve[temp]
                factors.add(p)
                while temp % p == 0:
                    temp //= p
            prime_factors_list.append(sorted(factors))

        # 初始化状态
        in_self = defaultdict(bool)
        divi_counts = defaultdict(int)
        current_total = 0
        answer = 0
        output = []

        for x in queries:
            idx = x-1  # queries是1-based
            num = a[idx]
            factors = prime_factors_list[idx]

            if in_self[idx]:
                # 移除操作
                sign = -1
                in_self[idx] = False
            else:
                # 添加操作
                sign = +1
                in_self[idx] = True

            # 计算当前贡献
            coprime_count = 0
            k = len(factors)
            for mask in range(1, 1 << k):
                d = 1
                bits = 0
                for i in range(k):
                    if mask & (1 << i):
                        d *= factors[i]
                        bits += 1
                cnt = divi_counts[d]
                coprime_count += cnt if bits % 2 else -cnt

            delta = sign * (current_total - coprime_count)
            answer += delta
            output.append(answer)

            # 更新除数计数
            for mask in cls._generate_divisors(num):
                divi_counts[mask] += sign

            current_total += sign

        return output

    @staticmethod
    def _build_sieve(max_num):
        sieve = list(range(max_num+1))
        for i in range(2, int(math.sqrt(max_num))+1):
            if sieve[i] == i:
                for j in range(i*i, max_num+1, i):
                    if sieve[j] == j:
                        sieve[j] = i
        return sieve

    @staticmethod
    def _generate_divisors(num):
        if num == 1:
            return []
        divisors = set()
        for i in range(2, int(math.isqrt(num)) + 1):
            if num % i == 0:
                divisors.update({i, num//i})
        divisors.add(num)
        return divisors
