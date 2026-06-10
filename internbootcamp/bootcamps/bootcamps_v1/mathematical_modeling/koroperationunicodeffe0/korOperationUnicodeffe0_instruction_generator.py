import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
from fractions import Fraction
import re




class Koroperationunicodeffe0InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicodeffe0 Bootcamp指令生成器"""
    
    def __init__(self, min_value=2, max_value=256, problem_types=None, allow_multilevel=True):
        """
        初始化Koroperationunicodeffe0指令生成器
        
        Args:
            min_value: 参数描述
            max_value: 参数描述
            problem_types: 参数描述
            allow_multilevel: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min = min_value
        self.max = max_value
        self.problem_types = problem_types or ['compute', 'solve']
        self.allow_multilevel = allow_multilevel
    
    def case_generator(self):
        problem_type = random.choice(self.problem_types)
        
        def generate_expressible():
            k = random.randint(1,4)
            b = random.randint(self.min, self.max)
            a = b ** k
            while a > self.max:
                k = random.randint(1,4)
                b = random.randint(self.min, self.max)
                a = b ** k
            return a, b, Fraction(k**2 +1, k)

        if problem_type == 'compute':
            if random.random() < 0.3:  
                a = random.randint(self.min, self.max)
                b = random.randint(self.min, self.max)
                while self.is_power(a, b) or a == b:
                    a = random.randint(self.min, self.max)
                    b = random.randint(self.min, self.max)
                return {
                    "type": "compute",
                    "expression": [a, b],
                    "log_expr": f"\\log_{{{b}}}{{{a}}} + \\log_{{{a}}}{{{b}}}",
                    "is_expressible": False
                }
            
            if self.allow_multilevel and random.random() < 0.5:
                a, base, frac = generate_expressible()
                m = random.randint(1,4)
                c = base ** m
                return {
                    "type": "compute",
                    "expression": [a, base, c],
                    "target": str(Fraction(m**2 +1, m)),
                    "is_expressible": True
                }
            else:
                a, b, frac = generate_expressible()
                return {
                    "type": "compute",
                    "expression": [a, b],
                    "target": f"{frac.numerator}/{frac.denominator}",
                    "is_expressible": True
                }
                
        else:  # solve类型完整实现
            # 生成单层求解案例
            position = random.choice([0, 1])
            X = random.randint(self.min, self.max)
            k = random.randint(1,4)
            if position == 0:
                b = X ** k
                equation = ['X', b]
            else:
                a = X ** k
                equation = [a, 'X']
            target = Fraction(k**2 +1, k)
            return {
                "type": "solve",
                "equation": equation,
                "target": f"{target.numerator}/{target.denominator}",
                "solution": X
            }
    
    @staticmethod
    def prompt_func(question_case):
        definition = """a￠b=\log_{b}{a}+\log_{a}{b}.
a and b are positive integers.
"""
        if question_case['type'] == 'compute':
            expr = '￠'.join(map(str, question_case['expression']))
            prompt = f"Compute {expr}.\n"
            if not question_case.get('is_expressible', True):
                prompt += "If the answer cannot be reduced to an integer or fraction then retain the form \\log_{b}{a}+\\log_{a}{b}.\n"
                prompt += "Please provide your answer in LaTeX format. "
            else:
                prompt += "If the answer is a fraction, write it in 'a/b' text format. Decimals are not allowed.\n"
            prompt += "Please wrap the answer in double square brackets, like this: [[your answer]]."
            return definition + prompt
        else:
            equation_str = '￠'.join(
                [str(x) if x != 'X' else 'X' for x in question_case['equation']]
            )
            prompt = f"If {equation_str} = {question_case['target']}, find X.\n"
            prompt += "The answer should only be given as a number.\n"
            prompt += "Please wrap the answer in double square brackets, like this: [[your answer]]."
            return definition + prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def is_power(a, b):
        """判断两个数是否互为整数幂"""
        if a == 1 or b == 1:
            return a == b
        try:
            exponent = math.log(a, b)
            return abs(exponent - round(exponent)) < 1e-10 and b**round(exponent) == a
        except ValueError:
            pass
        try:
            exponent = math.log(b, a)
            return abs(exponent - round(exponent)) < 1e-10 and a**round(exponent) == b
        except ValueError:
            return False
