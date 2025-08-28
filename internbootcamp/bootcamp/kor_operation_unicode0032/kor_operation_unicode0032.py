"""### 谜题描述
a♀b=(a+b)/2
a♂b=a×4+bExample questions are as follows:

<example 0>
Compute (3♀5)♂2.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute 7♂(6♀2)=32.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute (4♀8)♂3.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute 5♂(3♀7).
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
If (X♀3)♂2=22, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
If 4♂(X♀2)=30, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
If (X♀4)♂5=37, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
If 6♂(X♀3)=42, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
Now ignoring the previous rule.
Given that a♂b=a×4+b and 4♀3=3.5, compute 2♂(4♀3).
If the answer is a fraction, write it in 'a/b' text format.Decimals are not allowed.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
Now ignoring the previous rule.
Given that a♀b=(a+b)/2 and 5♂6=26, compute 5♂(4♀8).
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random  # 新增缺失的模块导入
from fractions import Fraction
from bootcamp import Basebootcamp

class KorOperationUnicode0032bootcamp(Basebootcamp):
    def __init__(self, min_val=1, max_val=20, equation_prob=0.5):
        self.min_val = min_val
        self.max_val = max_val
        self.equation_prob = equation_prob

    def case_generator(self):
        if random.random() < self.equation_prob:
            structure = random.choice(['struct1', 'struct2'])
            A = random.randint(self.min_val, self.max_val)
            B = random.randint(self.min_val, self.max_val)
            target_result = random.randint(self.min_val*2, self.max_val*2)

            if structure == 'struct1':
                x_val = Fraction(target_result - B, 2) - A
            else:
                fem_part = Fraction(A + B, 2)
                x_val = Fraction(target_result - fem_part, 4)
            
            return {
                'type': 'equation',
                'structure': structure,
                'A': A, 'B': B,
                'result': target_result,
                'correct_answer': {
                    'numerator': x_val.numerator,
                    'denominator': x_val.denominator
                }
            }
        else:
            structure = random.choice(['struct1', 'struct2'])
            a = random.randint(self.min_val, self.max_val)
            b = random.randint(self.min_val, self.max_val)
            c = random.randint(self.min_val, self.max_val)

            if structure == 'struct1':
                answer = 2*(a + b) + c
            else:
                answer = 4*a + Fraction(b + c, 2)
            
            return {
                'type': 'compute',
                'structure': structure,
                'a': a, 'b': b, 'c': c,
                'correct_answer': {
                    'numerator': answer.numerator,
                    'denominator': answer.denominator
                }
            }

    @staticmethod
    def prompt_func(question_case):
        operator_desc = (
            "You are given two custom operators: ♀ and ♂. The operator a♀b is defined as (a + b)/2, which calculates the average of a and b. "
            "The operator a♂b is defined as 4*a + b, which multiplies a by 4 and then adds b."
        )
        format_instruction = "Please wrap the answer in double square brackets like [[answer]]. Use a/b format for fractions."

        if question_case['type'] == 'compute':
            a, b, c = question_case['a'], question_case['b'], question_case['c']
            expr = f"({a}♀{b})♂{c}" if question_case['structure'] == 'struct1' else f"{a}♂({b}♀{c})"
            problem = f"Compute {expr}."
        else:
            A, B = question_case['A'], question_case['B']
            eq = f"(X♀{A})♂{B} = {question_case['result']}" if question_case['structure'] == 'struct1' else f"X♂({A}♀{B}) = {question_case['result']}"
            problem = f"If {eq}, find X."

        return f"{operator_desc}\n{problem}\n{format_instruction}"

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # Parse solution
            if '/' in solution:
                num, den = map(int, solution.split('/'))
                user_ans = Fraction(num, den)
            else:
                user_ans = Fraction(int(solution))
            
            # Get correct answer
            ans = identity['correct_answer']
            correct_ans = Fraction(ans['numerator'], ans['denominator'])
            
            return user_ans == correct_ans
        except (ValueError, ZeroDivisionError, KeyError):
            return False
