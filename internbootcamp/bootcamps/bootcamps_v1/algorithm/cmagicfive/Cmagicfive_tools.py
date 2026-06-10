import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cmagicfive.Cmagicfive_reward_calculator import CmagicfiveRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CmagicfiveVerificationTool(BaseTool):
    """Cmagicfive验证工具"""
    
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
            score = CmagicfiveRewardCalculator.verify_score(
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
            logger.error(f"CmagicfiveVerificationTool执行错误: {str(e)}")
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
    def _gen_has_05(self):
        length = random.randint(self.a_min_length, self.a_max_length)
        chars = []
        for _ in range(length):
            if random.random() < 0.3:
                chars.append(random.choice(['0', '5']))
            else:
                chars.append(random.choice('12346789'))
        if not any(c in {'0','5'} for c in chars):
            chars[random.randint(0, len(chars)-1)] = random.choice(['0','5'])
        return ''.join(chars)

    def _gen_random(self):
        length = random.randint(self.a_min_length, self.a_max_length)
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def compute_ways(a, k):
        MOD = 10**9 + 7
        if not a:
            return 0

        l = len(a)
        two_l = pow(2, l, MOD)
        denominator = (two_l - 1) % MOD
        inv_denominator = pow(denominator, MOD-2, MOD) if denominator != 0 else 0

        power_sum = pow(two_l, k, MOD)

        base_sum = 0
        pwr = 1  # 对应2^0
        for char in a:
            if char in {'0', '5'}:
                base_sum = (base_sum + pwr) % MOD
            pwr = (pwr * 2) % MOD

        if inv_denominator == 0:
            total = 0
        else:
            numerator = (base_sum * (power_sum - 1 + MOD)) % MOD
            total = (numerator * inv_denominator) % MOD
        return total
