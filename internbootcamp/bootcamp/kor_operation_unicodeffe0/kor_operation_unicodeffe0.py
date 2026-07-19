"""### 谜题描述
a￠b=\log_{b}{a}+\log_{a}{b}.
a and b are positive integers.Example questions are as follows:

<example 0>
Compute 2￠8.
If the answer is a fraction, write it in 'a/b' text format.Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute 3￠9.
If the answer is a fraction, write it in 'a/b' text format.Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute 2￠2￠4.
If the answer is a fraction, write it in 'a/b' text format.Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute 5￠8.
If the answer cannot be reduced to an integer or fraction then retain the form \log_{b}{a}+\log_{a}{b}.
Please provide your answer in LaTeX format. Please wrap the answer in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
Compute 16￠256.
If the answer is a fraction, write it in 'a/b' text format.Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
Compute 9￠243.
If the answer is a fraction, write it in 'a/b' text format.Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
If 512￠X=82/9, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
If 3￠X=17/4, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
If X￠256=73/24, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
If 3￠3￠X=5/2, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import math
from fractions import Fraction
import re
from bootcamp import Basebootcamp

class KorOperationUnicodeffe0bootcamp(Basebootcamp):
    def __init__(self, min_value=2, max_value=256, problem_types=None, allow_multilevel=True):
        self.min = min_value
        self.max = max_value
        self.problem_types = problem_types or ['compute', 'solve']
        self.allow_multilevel = allow_multilevel

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

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1] if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if identity['type'] == 'compute':
                if identity.get('is_expressible', True):
                    return Fraction(solution) == Fraction(identity['target'])
                else:
                    given = re.sub(r'\s+', '', solution)
                    expected = re.sub(r'\s+', '', identity['log_expr'])
                    return given == expected
            else:
                return int(solution) == identity['solution']
        except:
            return False
