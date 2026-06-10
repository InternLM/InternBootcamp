import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.koroperationunicodeffe1.korOperationUnicodeffe1_reward_calculator import Koroperationunicodeffe1RewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Koroperationunicodeffe1VerificationTool(BaseTool):
    """Koroperationunicodeffe1验证工具"""
    
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
            score = Koroperationunicodeffe1RewardCalculator.verify_score(
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
            logger.error(f"Koroperationunicodeffe1VerificationTool执行错误: {str(e)}")
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
    def generate_finite_case(self):
        element_type = self.element_type
        if element_type == 'mixed':
            element_type = random.choice(['number', 'letter'])

        size_A = random.randint(2, self.max_size)
        size_B = random.randint(2, self.max_size)

        if element_type == 'number':
            elements = list(range(1, 21))
            A = sorted(random.sample(elements, size_A))
            B = sorted(random.sample(elements, size_B))
        else:
            letters = [chr(ord('a') + i) for i in range(26)]
            A = sorted(random.sample(letters, size_A))
            B = sorted(random.sample(letters, size_B))

        A_set = set(A)
        B_set = set(B)
        solution = sorted(list(A_set.symmetric_difference(B_set)))
        return {
            'type': 'finite',
            'A': A,
            'B': B,
            'solution': solution
        }

    def generate_interval_case(self):
        template = random.choice([1, 2, 3])
        if template == 1:  # 非重叠区间
            a = random.randint(-5, 3)
            b = a + random.randint(2, 4)
            while True:
                c = random.randint(b+1, b+3)
                if c > b: break
            A_desc = f'x > {a}'
            B_desc = f'x < {b}'
            solution = f'{{x | x ≤ {a} or x ≥ {b}}}'
        elif template == 2:  # 包含区间
            a = random.randint(2, 5)
            b = random.randint(-3, a-1)
            A_desc = f'x < {a}'
            B_desc = f'x > {b}'
            solution = f'{{x | x ≤ {b} or x ≥ {a}}}'
        else:  # 二次不等式
            c = random.randint(1, 3)
            A_desc = 'x is a real number'
            B_desc = f'x² < {c**2}'
            solution = f'{{x | x ≤ -{c} or x ≥ {c}}}'
        return {
            'type': 'interval',
            'A': A_desc,
            'B': B_desc,
            'solution': solution
        }

    def generate_special_case(self):
        case_type = random.choice([1, 2])
        if case_type == 1:  # 自然数 vs 正整数
            return {
                'type': 'special',
                'A': 'x is a natural number (including 0)',
                'B': 'x is a positive integer',
                'solution': '{0}'
            }
        else:  # 全体实数 vs 空集
            return {
                'type': 'special',
                'A': 'x is a real number',
                'B': 'x is an element of empty set',
                'solution': '{x | x ∈ ℝ}'
            }
