import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cphoenixanddistribution.Cphoenixanddistribution_reward_calculator import CphoenixanddistributionRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import Counter



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CphoenixanddistributionVerificationTool(BaseTool):
    """Cphoenixanddistribution验证工具"""
    
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
            score = CphoenixanddistributionRewardCalculator.verify_score(
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
            logger.error(f"CphoenixanddistributionVerificationTool执行错误: {str(e)}")
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
    def _generate_random_case(self):
        n = random.randint(self.min_length, self.max_length)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        k = random.randint(1, max(1, n//2)) if n > 1 else 1
        return {'n': n, 'k': k, 's': s}

    def _generate_edge_case(self):
        case_type = random.choice([1, 2, 3, 4])

        if case_type == 1:  # k=1的特殊情况
            s = ''.join(sorted(random.choices(string.ascii_lowercase, k=random.randint(5, 10))))
            return {'n': len(s), 'k': 1, 's': s}

        elif case_type == 2:  # 所有字符相同的情况
            char = random.choice(string.ascii_lowercase)
            n = random.randint(5, 15)
            k = random.randint(1, n)
            return {'n': n, 'k': k, 's': char * n}

        elif case_type == 3:  # 需要均匀分配的情况
            base_char = random.choice(string.ascii_lowercase)
            other_char = chr(ord(base_char) + 1)
            s = base_char * 5 + other_char * 10
            k = random.randint(3, 5)
            return {'n': len(s), 'k': k, 's': ''.join(random.sample(s, len(s)))}

        else:  # 首字符不满足k需求的情况
            first_char = 'a'
            rest_chars = ''.join(random.choices(string.ascii_lowercase[1:], k=random.randint(8, 15)))
            s = first_char * 3 + rest_chars
            k = 5  # 大于首字符数量(3)
            return {'n': len(s), 'k': k, 's': ''.join(random.sample(s, len(s)))}

    @classmethod
    def compute_correct_answer(cls, s, k):
        sorted_s = ''.join(sorted(s))
        n = len(sorted_s)
        first_char_count = sorted_s.count(sorted_s[0])

        if first_char_count < k or n == k:
            return sorted_s[k-1]
        else:
            if sorted_s[k] != sorted_s[-1]:
                return sorted_s[0] + sorted_s[k:]
            else:
                repeat = (n - 1) // k
                return sorted_s[0] + sorted_s[-1] * repeat

    @staticmethod
    def split_into_parts(sorted_s, k):
        # 辅助方法用于验证分割逻辑
        parts = []
        if Counter(sorted_s) == Counter(sorted_s[0]*len(sorted_s)):
            base = sorted_s[0]
            per_part = len(sorted_s) // k
            remainder = len(sorted_s) % k
            for i in range(k):
                parts.append(base * (per_part + (1 if i < remainder else 0)))
        else:
            parts = [sorted_s[0]] * k
            remaining = sorted_s[k:]
            for i in range(len(remaining)):
                parts[i % k] += remaining[i]
            parts = [''.join(sorted(p)) for p in parts]
        return parts
