from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.bbehbooleanexpressions.bbehbooleanexpressions_reward_calculator import BbehbooleanexpressionsRewardCalculator

# 导入依赖库
import re
import random
import math
from itertools import count




class BbehbooleanexpressionsInteraction(BaseInteraction):
    """Bbehbooleanexpressions交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = BbehbooleanexpressionsRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个bbehbooleanexpressions问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
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
