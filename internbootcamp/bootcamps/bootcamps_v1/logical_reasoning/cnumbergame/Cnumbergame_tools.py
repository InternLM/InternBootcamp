import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cnumbergame.Cnumbergame_reward_calculator import CnumbergameRewardCalculator

# 导入依赖库
import re
import math
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CnumbergameVerificationTool(BaseTool):
    """Cnumbergame验证工具"""
    
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
            score = CnumbergameRewardCalculator.verify_score(
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
            logger.error(f"CnumbergameVerificationTool执行错误: {str(e)}")
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
    def _generate_odd_prime(self, min_p=3, max_p=None):
        max_p = max_p or self.max_n // 2
        if min_p % 2 == 0:
            min_p += 1
        attempts = 0
        while attempts < 1000:
            p = random.randint(min_p, max_p)
            if p % 2 == 0:
                continue
            if self.is_prime(p):
                return p
            attempts += 1
        return 3  # fallback

    def _generate_odd_composite(self, min_val=9, max_val=None):
        max_val = max_val or self.max_n // 2
        while True:
            num = random.randint(min_val, max_val)
            if num % 2 == 0:
                continue
            if not self.is_prime(num):
                return num

    @staticmethod
    def is_prime(num):
        if num < 2:
            return False
        if num % 2 == 0:
            return num == 2
        for i in range(3, int(math.isqrt(num)) + 1, 2):
            if num % i == 0:
                return False
        return True

    @staticmethod
    def get_correct_answer(n):
        original_n = n
        t = 0
        while n % 2 == 0:
            n = n // 2
            t += 1
        k = n

        if t == 0:
            return "FastestFinger" if k == 1 else "Ashishgup"
        elif t == 1:
            if k == 1:
                return "Ashishgup"
            is_prime = Cnumbergamebootcamp.is_prime(k)
            return "FastestFinger" if is_prime else "Ashishgup"
        else:
            return "FastestFinger" if k == 1 else "Ashishgup"
