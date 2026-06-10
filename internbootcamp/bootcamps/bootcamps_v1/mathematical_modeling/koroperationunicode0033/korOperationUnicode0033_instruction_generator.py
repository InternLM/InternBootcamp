import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import re
import random
from typing import Optional




class Koroperationunicode0033InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode0033 Bootcamp指令生成器"""
    
    def __init__(self, compute_prob=0.5, max_square=10, operand_range=(1,5), max_depth=2):
        """
        初始化Koroperationunicode0033指令生成器
        
        Args:
            compute_prob: 参数描述
            max_square: 参数描述
            operand_range: 参数描述
            max_depth: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.compute_prob = compute_prob
        self.max_square = max_square
        self.operand_range = operand_range
        self.max_depth = max_depth  # 控制嵌套层级
    
    def case_generator(self):
        if random.random() < self.compute_prob:
            # 生成带随机嵌套结构的计算题
            def build_expression(depth=0):
                # 基础情况：返回数字或创建新表达式
                if depth >= self.max_depth:
                    return random.randint(1, self.max_square) ** 2
                
                # 随机决定是否创建嵌套结构
                if random.random() < 0.5:
                    # 创建新的运算符节点
                    op = random.choice(['①', '②'])
                    left = build_expression(depth + 1)
                    right = build_expression(depth + 1)
                    return {'operator': op, 'left': left, 'right': right}
                else:
                    # 返回基本数字
                    return random.randint(1, self.max_square) ** 2
            
            return {
                'type': 'compute',
                'expression': build_expression()
            }
        else:
            # 生成解方程题（保持原逻辑）
            a = random.randint(1, self.operand_range[1])
            m = random.randint(a+1, a+5)
            X = (m**2 - a**2) ** 2
            b = random.randint(1, self.operand_range[1])
            c = m * b
            return {
                'type': 'solve',
                'equation': {'a': a, 'b': b, 'c': c},
                'X': X
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        definition = """a①b=\sqrt{a}+b^2.
a②b=\sqrt{a}×b.
"""
        if question_case['type'] == 'compute':
            expr_str = KorOperationUnicode0033bootcamp.expression_to_str(question_case['expression'])
            latex_rules = ("Please provide your answer in LaTeX format. "
                           "Use \\frac{a}{b} for fractions and \\sqrt{x} for roots. "
                           "Put your final answer within [[ ]].")
            return definition + f"Compute {expr_str}.\n{latex_rules}"
        else:
            eq = question_case['equation']
            return definition + (f"If (X①{eq['a']})②{eq['b']} = {eq['c']}, find X.\n"
                    "Provide only a numeric answer within [[ ]].") 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def expression_to_str(expr) -> str:
        if isinstance(expr, dict):
            left = KorOperationUnicode0033bootcamp.expression_to_str(expr['left'])
            right = KorOperationUnicode0033bootcamp.expression_to_str(expr['right'])
            return f"({left}{expr['operator']}{right})"
        return str(expr)

    @staticmethod
    def compute_expression(expr) -> float:
        if isinstance(expr, dict):
            left = KorOperationUnicode0033bootcamp.compute_expression(expr['left'])
            right = KorOperationUnicode0033bootcamp.compute_expression(expr['right'])
            if expr['operator'] == '①':
                return math.sqrt(left) + right**2
            return math.sqrt(left) * right
        return float(expr)

    @staticmethod
    def parse_solution(solution: str) -> float:
        solution = solution.replace(' ', '')
        # 处理分数
        frac_match = re.match(r'\\frac\{(-?\d+)\}\{(\d+)\}', solution)
        if frac_match:
            return float(frac_match[1]) / float(frac_match[2])

        # 处理根号表达式（支持系数）
        sqrt_match = re.match(r'(-?)(\d*)\\sqrt\{(\d+)\}', solution)
        if sqrt_match:
            sign = -1 if sqrt_match[1] else 1
            coeff = float(sqrt_match[2] or 1) * sign
            return coeff * math.sqrt(float(sqrt_match[3]))

        # 处理纯根号
        if solution.startswith('\\sqrt'):
            return math.sqrt(float(re.search(r'\d+', solution).group()))

        return float(solution)
