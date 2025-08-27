"""### 谜题描述
a◇b= a^b.
a and b are positive integers.Example questions are as follows:

<example 0>
Compute 5◇1.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute 2◇4.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute 2◇3◇2.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute 4◇2◇3.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
If X◇2=64, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
If 3◇X=27, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
If X◇3=125, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
If X◇3◇3=512, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
If 3◇X=243, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
If 5◇2◇X=625, find X.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from functools import reduce
from operator import mul
from bootcamp import Basebootcamp

class KorOperationUnicode25c7bootcamp(Basebootcamp):
    def __init__(self, min_value=1, max_value=10, min_operands=2, max_operands=3, solve_x_ratio=0.5):
        # 参数有效性校验
        if min_value < 1:
            raise ValueError("min_value must be at least 1")
        if max_value < min_value:
            raise ValueError("max_value must be >= min_value")
        if min_operands < 2:
            raise ValueError("min_operands must be at least 2")
        if max_operands < min_operands:
            raise ValueError("max_operands must be >= min_operands")
        if not (0 <= solve_x_ratio <= 1):
            raise ValueError("solve_x_ratio must be between 0 and 1")
        
        self.min_value = min_value
        self.max_value = max_value
        self.min_operands = min_operands
        self.max_operands = max_operands
        self.solve_x_ratio = solve_x_ratio

    def case_generator(self):
        if random.random() < self.solve_x_ratio:
            return self._generate_solve_x_case()
        return self._generate_compute_case()

    def _generate_compute_case(self):
        # 确保操作数数量在有效范围内
        n_operands = random.randint(self.min_operands, self.max_operands)
        operands = [random.randint(self.min_value, self.max_value) for _ in range(n_operands)]
        
        # 右结合幂运算计算
        try:
            result = reduce(lambda a, b: b ** a, reversed(operands))
        except OverflowError:
            # 处理极大数值异常，重新生成合理数值
            return self._generate_compute_case()
        
        return {
            'type': 'compute',
            'operands': operands,
            'result': result
        }

    def _generate_solve_x_case(self):
        # 确保至少有一个其他操作数
        n_other_operands = random.randint(1, self.max_operands-1)
        other_operands = [random.randint(self.min_value, self.max_value) for _ in range(n_other_operands)]
        exponent = reduce(mul, other_operands, 1)
        
        # 生成有效解X
        x_val = random.randint(self.min_value, self.max_value)
        result = x_val ** exponent
        
        return {
            'type': 'solve_x',
            'other_operands': other_operands,
            'x_value': x_val,
            'result': result,
            'exponent': exponent
        }

    @staticmethod
    def prompt_func(question_case):
        prefix = """a◇b means a raised to the power of b (a^b).

The diamond operator is right-associative, meaning:
a◇b◇c = a◇(b◇c) = a^(b^c)

"""
        if question_case['type'] == 'compute':
            expression = '◇'.join(map(str, question_case['operands']))
            return prefix + f"计算表达式 {expression} 的值。答案必须为单独的数字并用双方括号包裹，例如：[[答案]]。"
        else:
            other_ops = '◇'.join(map(str, question_case['other_operands']))
            return prefix + f"若 X◇{other_ops} = {question_case['result']}，求 X 的值。答案必须为单独的数字并用双方括号包裹，例如：[[答案]]。"

    @staticmethod
    def extract_output(output):
        # 匹配所有可能的答案格式，包括中英文括号
        matches = re.findall(r'\[\[(\d+)\]\]|【【(\d+)】】', output)
        # 优先取最后一个匹配的数字，支持多语言格式
        last_match = matches[-1] if matches else None
        return last_match[0] or last_match[1] if last_match else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 支持字符串和数字类型的比较
            solution_num = int(solution) if isinstance(solution, str) else solution
        except (ValueError, TypeError):
            return False
        
        # 验证数据结构完整性
        if identity['type'] not in ('compute', 'solve_x'):
            return False
            
        if identity['type'] == 'compute':
            return solution_num == identity.get('result', None)
        else:
            return solution_num == identity.get('x_value', None)
