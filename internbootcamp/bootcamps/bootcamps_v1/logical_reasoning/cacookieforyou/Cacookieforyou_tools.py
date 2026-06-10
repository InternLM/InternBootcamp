import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cacookieforyou.Cacookieforyou_reward_calculator import CacookieforyouRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CacookieforyouVerificationTool(BaseTool):
    """Cacookieforyou验证工具"""
    
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
            score = CacookieforyouRewardCalculator.verify_score(
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
            logger.error(f"CacookieforyouVerificationTool执行错误: {str(e)}")
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
    def _generate_zero_cookie_case(self):
        """确保至少有一个客人存在"""
        a, b = 0, 0
        while True:
            n = random.randint(0, self.max_value)
            m = random.randint(0, self.max_value)
            if n + m > 0:
                return {'a': a, 'b': b, 'n': n, 'm': m}

    def _generate_single_type_guest_case(self):
        """确保至少有一类客人存在"""
        while True:
            if random.random() < 0.5:
                case = {
                    'a': random.randint(0, self.max_value),
                    'b': random.randint(0, self.max_value),
                    'n': random.randint(0, self.max_value),
                    'm': 0
                }
            else:
                case = {
                    'a': random.randint(0, self.max_value),
                    'b': random.randint(0, self.max_value),
                    'n': 0,
                    'm': random.randint(0, self.max_value)
                }
            if case['n'] + case['m'] > 0:
                return case

    def _generate_yes_case(self):
        """添加重试机制防止死循环"""
        for _ in range(self.max_retries):
            a = random.randint(0, self.max_value)
            b = random.randint(0, self.max_value)
            if a + b == 0:
                continue

            a_new, b_new = max(a, b), min(a, b)
            max_m = b_new
            m = random.randint(0, max_m)
            remaining = (a_new + b_new) - m
            n = random.randint(0, remaining)

            if n + m > 0:
                return {'a': a, 'b': b, 'n': n, 'm': m}
        # 保底生成合法案例
        return {'a': 2, 'b': 1, 'n': 1, 'm': 1}

    def _generate_no_case(self):
        strategies = [
            self._generate_case_total_exceed,
            self._generate_case_m_exceed,
            self._generate_zero_cookie_angry_case
        ]
        return random.choice(strategies)()

    def _generate_case_total_exceed(self):
        for _ in range(self.max_retries):
            a = random.randint(1, self.max_value)
            b = random.randint(1, self.max_value)
            total = a + b
            min_guest = total + 1
            n = random.randint(0, min_guest)
            m = min_guest - n
            if m < 0:
                m = 0
                n = min_guest
            if a + b < n + m:
                return {'a': a, 'b': b, 'n': n, 'm': m}
        return {'a': 1, 'b': 1, 'n': 2, 'm': 1}

    def _generate_case_m_exceed(self):
        for _ in range(self.max_retries):
            a = random.randint(0, self.max_value)
            b = random.randint(0, self.max_value)
            a_new, b_new = max(a, b), min(a, b)
            if b_new == 0:
                continue
            m = random.randint(b_new + 1, self.max_value)
            remaining = (a_new + b_new) - m
            n = random.randint(0, max(remaining, 0))
            if (n + m) <= (a_new + b_new):
                return {'a': a, 'b': b, 'n': n, 'm': m}
        return {'a': 3, 'b': 1, 'n': 1, 'm': 3}

    def _generate_zero_cookie_angry_case(self):
        return {'a': 0, 'b': 0, 
                'n': random.randint(1, self.max_value),
                'm': random.randint(0, self.max_value)}
