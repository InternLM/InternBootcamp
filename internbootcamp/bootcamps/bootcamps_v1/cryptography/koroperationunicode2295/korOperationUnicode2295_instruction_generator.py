import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class Koroperationunicode2295InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode2295 Bootcamp指令生成器"""
    
    def __init__(self, max_operand=10, equation_prob=0.5, allow_division=True):
        """
        初始化Koroperationunicode2295指令生成器
        
        Args:
            max_operand: 参数描述
            equation_prob: 参数描述
            allow_division: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_operand = max_operand
        self.equation_prob = equation_prob
        self.allow_division = allow_division
    
    def case_generator(self):
        if random.random() < self.equation_prob:
            return self._generate_equation_case()
        else:
            return self._generate_compute_case()
    
    @staticmethod
    def prompt_func(question_case):
        definition = "a⊕b=a+bi.\n"
        if question_case['type'] == 'compute':
            left = f"({question_case['left_a']}⊕{question_case['left_b']})"
            right = f"({question_case['right_a']}⊕{question_case['right_b']})"
            expr = f"{left} {question_case['operator']} {right}"
            return definition + f"Compute {expr}. If the answer is a complex number, write it in the form x + yi. Please wrap your answer in double square brackets, like this: [[answer]]."
        else:
            left_operand = question_case['left_operands'][0]
            right_operand = question_case['left_operands'][1]
            left = f"({left_operand['a']}⊕{left_operand['b']})"
            right = f"({right_operand['a']}⊕{right_operand['b']})"
            expr = f"{left} {question_case['operator']} {right}"
            target_real = question_case['target_real']
            target_imag = question_case['target_imag']
            
            # 显示优化
            if isinstance(target_real, float) and target_real.is_integer():
                target_real = int(target_real)
            if isinstance(target_imag, float) and target_imag.is_integer():
                target_imag = int(target_imag)
            
            if target_imag == 0:
                target_str = f"{target_real}"
            else:
                imag_abs = abs(target_imag)
                imag_sign = '+' if target_imag > 0 else '-'
                target_str = f"{target_real} {imag_sign} {imag_abs}i"
            
            return definition + f"If {expr} = {target_str}, find X. The answer should only be given as a number. Please wrap your answer in double square brackets, like this: [[answer]]." 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_equation_case(self):
        operators = ['+', '-', '*']
        if self.allow_division:
            operators.append('/')

        for _ in range(100):
            x = random.uniform(-self.max_operand, self.max_operand)
            x = round(x, 1)  # 允许一位小数
            operand_index = random.choice([0, 1])
            part = random.choice(['a', 'b'])

            left_a = random.randint(-self.max_operand, self.max_operand)
            left_b = random.randint(-self.max_operand, self.max_operand)
            right_a = random.randint(-self.max_operand, self.max_operand)
            right_b = random.randint(-self.max_operand, self.max_operand)
            operator = random.choice(operators)

            if operand_index == 0:
                left_operand = {'a': 'X' if part == 'a' else left_a, 'b': 'X' if part == 'b' else left_b}
                right_operand = {'a': right_a, 'b': right_b}
                a1 = x if part == 'a' else left_a
                b1 = x if part == 'b' else left_b
                a2, b2 = right_a, right_b
            else:
                left_operand = {'a': left_a, 'b': left_b}
                right_operand = {'a': 'X' if part == 'a' else right_a, 'b': 'X' if part == 'b' else right_b}
                a1, b1 = left_a, left_b
                a2 = x if part == 'a' else right_a
                b2 = x if part == 'b' else right_b

            # 处理分母有效性
            if operator == '/':
                if (a2 == 0 and b2 == 0):
                    continue
                denominator = a2**2 + b2**2
                if denominator == 0:
                    continue

            try:
                if operator == '+':
                    target_real = a1 + a2
                    target_imag = b1 + b2
                elif operator == '-':
                    target_real = a1 - a2
                    target_imag = b1 - b2
                elif operator == '*':
                    target_real = a1 * a2 - b1 * b2
                    target_imag = a1 * b2 + b1 * a2
                else:
                    denominator = a2**2 + b2**2
                    target_real = (a1 * a2 + b1 * b2) / denominator
                    target_imag = (b1 * a2 - a1 * b2) / denominator

                # 允许浮点结果，保留两位小数
                target_real = round(target_real, 2)
                target_imag = round(target_imag, 2)

                return {
                    'type': 'equation',
                    'left_operands': [left_operand, right_operand],
                    'operator': operator,
                    'target_real': target_real,
                    'target_imag': target_imag,
                    'unknown': {'operand_index': operand_index, 'part': part},
                    'solution': round(x, 2)
                }
            except:
                continue
        return self._generate_compute_case()

    def _generate_compute_case(self):
        operators = ['+', '-', '*']
        if self.allow_division:
            operators.append('/')

        operator = random.choice(operators)

        for _ in range(100):
            a = random.randint(-self.max_operand, self.max_operand)
            b = random.randint(-self.max_operand, self.max_operand)
            c = random.randint(-self.max_operand, self.max_operand)
            d = random.randint(-self.max_operand, self.max_operand)

            if operator == '/' and (c == 0 and d == 0):
                continue

            if operator == '+':
                real = a + c
                imag = b + d
            elif operator == '-':
                real = a - c
                imag = b - d
            elif operator == '*':
                real = a * c - b * d
                imag = a * d + b * c
            else:
                denominator = c**2 + d**2
                real = (a * c + b * d) / denominator
                imag = (b * c - a * d) / denominator

            # 保留两位小数
            real = round(real, 2)
            imag = round(imag, 2)

            return {
                'type': 'compute',
                'operator': operator,
                'left_a': a,
                'left_b': b,
                'right_a': c,
                'right_b': d,
                'solution_real': real,
                'solution_imag': imag
            }

        return {
            'type': 'compute',
            'operator': '+',
            'left_a': random.randint(-self.max_operand, self.max_operand),
            'left_b': random.randint(-self.max_operand, self.max_operand),
            'right_a': random.randint(-self.max_operand, self.max_operand),
            'right_b': random.randint(-self.max_operand, self.max_operand),
            'solution_real': 0,
            'solution_imag': 0
        }
