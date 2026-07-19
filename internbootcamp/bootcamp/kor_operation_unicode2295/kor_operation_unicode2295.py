"""### 谜题描述
a⊕b=a+bi.Example questions are as follows:

<example 0>
Compute (3⊕4)+(2⊕1).
If the answer is a complex number, write it in the form x + yi.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute (5⊕2)−(3⊕1)
If the answer is a complex number, write it in the form x + yi.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute (2⊕3)×(1⊕4).
If the answer is a complex number, write it in the form x + yi.
The answer may be negative, if so write it in a format such as '-5'.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute (4⊕2)/(2⊕1).
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
Compute (6⊕3)+(1⊕2)×2.
If the answer is a complex number, write it in the form x + yi.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
Compute 3×(2⊕1)−(1⊕3).
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
If (X⊕2)+(1⊕3)=4+5i, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
If (3⊕Y)−(2⊕1)=1+3i Find Y
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
If (2⊕3)×(1⊕X)=−10+11i, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
If (6⊕3)+(X⊕2)×2=10+11i, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random
from bootcamp import Basebootcamp

class KorOperationUnicode2295bootcamp(Basebootcamp):
    def __init__(self, max_operand=10, equation_prob=0.5, allow_division=True):
        self.max_operand = max_operand
        self.equation_prob = equation_prob
        self.allow_division = allow_division
    
    def case_generator(self):
        if random.random() < self.equation_prob:
            return self._generate_equation_case()
        else:
            return self._generate_compute_case()
    
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
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return re.sub(r'\s+', '', last_match)  # 移除所有空格
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        def parse_complex(s):
            s = s.replace(' ', '').lower().replace('i', 'j')
            try:
                c = complex(s)
                return (round(c.real, 2), round(c.imag, 2))
            except:
                return (None, None)
        
        if identity['type'] == 'equation':
            try:
                user_value = round(float(solution), 2)
                return user_value == identity['solution']
            except:
                return False
        else:
            real, imag = parse_complex(solution)
            if real is None or imag is None:
                return False
            target_real = round(identity['solution_real'], 2)
            target_imag = round(identity['solution_imag'], 2)
            return (real == target_real) and (imag == target_imag)
