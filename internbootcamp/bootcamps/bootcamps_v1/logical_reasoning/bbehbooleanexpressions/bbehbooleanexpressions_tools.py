import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.bbehbooleanexpressions.bbehbooleanexpressions_reward_calculator import BbehbooleanexpressionsRewardCalculator

# 导入依赖库
import re
import random
import math
from itertools import count



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BbehbooleanexpressionsVerificationTool(BaseTool):
    """Bbehbooleanexpressions验证工具"""
    
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
            score = BbehbooleanexpressionsRewardCalculator.verify_score(
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
            logger.error(f"BbehbooleanexpressionsVerificationTool执行错误: {str(e)}")
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
    def _generate_math_expression(self):
        """Generate a mathematical expression that evaluates to True or False."""
        operators = ['greater than', 'is less than or equal to', 'is greater than', '<=', '>']

        # Generate random numbers
        a = random.randint(-10, 10)
        b = random.randint(-10, 10)
        c = random.randint(-10, 10)
        d = random.randint(-10, 10)

        # Randomly choose expression type
        expr_type = random.choice([
            f"{a} * {b} + {c} * {d} is less than or equal to {random.randint(-10, 10)} * {random.randint(-10, 10)}",
            f"{a} * {b} > {c}",
            f"{a} - ({b} / {c}) is greater than {d}",
            f"{a} - ({b} / {c}) <= {d}",
            f"max({a}, {b}, {c}, {d}) - min({a}, {b}, {c}, {d}) is greater than {random.randint(1, 10)}",
            f"max({a}, {b}, {c}, {d}) - min({a}, {b}, {c}, {d}) <= {random.randint(1, 10)}"
        ])

        return expr_type

    def _generate_capital_fact(self, is_true=True):
        """Generate a statement about a country's capital that is either true or false."""
        country = random.choice(list(self.capital_facts.keys()))

        if is_true:
            return f"The capital of {country} is {self.capital_facts[country]}."
        else:
            false_capital = random.choice(self.false_capitals[country])
            return f"The capital of {country} is {false_capital}."

    def _generate_atomic_expr(self, target_value=None):
        """Generate a simple atomic expression with a specified truth value."""
        if target_value is None:
            # If no target value specified, randomly choose True or False
            return random.choice([True, False])

        if target_value:
            # Generate a True statement
            expr_type = random.choice(['bool', 'capital', 'math'])
            if expr_type == 'bool':
                return "True"
            elif expr_type == 'capital':
                return self._generate_capital_fact(is_true=True)
            else:
                # Create a mathematical expression that evaluates to True
                # This requires more careful construction to ensure it's True
                a = random.randint(1, 10)
                return f"{a} * {a} > {a}"
        else:
            # Generate a False statement
            expr_type = random.choice(['bool', 'capital', 'math'])
            if expr_type == 'bool':
                return "False"
            elif expr_type == 'capital':
                return self._generate_capital_fact(is_true=False)
            else:
                # Create a mathematical expression that evaluates to False
                a = random.randint(1, 10)
                return f"{a} * {-a} > {a * a}"

    def _generate_expression(self, depth=0, target_value=None):
        """
        Generate a boolean expression with a target truth value.

        Args:
            depth: Current depth of the expression tree
            target_value: Desired truth value of the expression

        Returns:
            tuple: (expression string, actual truth value)
        """
        if depth >= self.max_depth or random.random() < 0.3:
            # Base case: return an atomic expression
            if isinstance(target_value, bool):
                return self._generate_atomic_expr(target_value), target_value
            else:
                val = bool(random.getrandbits(1))
                return self._generate_atomic_expr(val), val

        # Choose an operator
        operator = random.choice(['and', 'or', 'not'])

        if operator == 'not':
            # For NOT, we need the opposite of our target value
            if isinstance(target_value, bool):
                sub_target = not target_value
            else:
                sub_target = bool(random.getrandbits(1))

            sub_expr, sub_val = self._generate_expression(depth + 1, sub_target)
            expr = f"not ({sub_expr})"
            return expr, not sub_val

        else:  # 'and' or 'or'
            if operator == 'and':
                # For AND to be True, both operands must be True
                if target_value:
                    left_target = True
                    right_target = True
                else:
                    # For AND to be False, at least one operand must be False
                    if random.random() < 0.5:
                        left_target = False
                        right_target = random.choice([True, False])
                    else:
                        left_target = random.choice([True, False])
                        right_target = False
            else:  # 'or'
                # For OR to be True, at least one operand must be True
                if target_value:
                    if random.random() < 0.5:
                        left_target = True
                        right_target = random.choice([True, False])
                    else:
                        left_target = random.choice([True, False])
                        right_target = True
                else:
                    # For OR to be False, both operands must be False
                    left_target = False
                    right_target = False

            left_expr, left_val = self._generate_expression(depth + 1, left_target)
            right_expr, right_val = self._generate_expression(depth + 1, right_target)

            if operator == 'and':
                result_val = left_val and right_val
            else:
                result_val = left_val or right_val

            expr = f"({left_expr}) {operator} ({right_expr})"
            return expr, result_val

    def _generate_complex_expression(self, target_value):
        """Generate a more complex boolean expression for the puzzle."""
        # Start with a simple expression
        expr, actual_val = self._generate_expression(0, target_value)

        # Add more complexity with nested not operations
        if random.random() < 0.7:
            not_count = random.randint(1, 3)
            for _ in range(not_count):
                expr = f"not not {expr}"
                # Double negation doesn't change the value

        return expr, actual_val
