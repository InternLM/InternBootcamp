"""### 谜题描述
1.Give a set of operation symbols.
2.Find the correct number from numbers 0 through 9 to make the equation equal to the given number.
3.Follow the normal order of operations.Example questions are as follows:

<example 0>
?+?*?-?=10
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a+b*c-d=10]].
</example 0>

<example 1>
?-?+?+?=2
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a-b+c+d=2]].
</example 1>

<example 2>
?/?+?+?=12
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a/b+c+d=12]].
</example 2>

<example 3>
?+?+?*?=28
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a+b+c*d=28]].
</example 3>

<example 4>
?/?+?*?+?=14
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a/b+c*d+e=14]].
</example 4>

<example 5>
?-?+?+?/?=6
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a-b+c+d/e=6]].
</example 5>

<example 6>
?/?+?+?+?=17
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a/b+c+d+e=17]].
</example 6>

<example 7>
?*?+?+?/?=46
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a*b+c+d/e=46]].
</example 7>

<example 8>
?/?+?/?-?-?=-5
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a/b+c/d-e-f=-5]].
</example 8>

<example 9>
?*?*?+?-?*?=125
There may be many solutions, end by citing a feasible solution.
Provide the equation with values filled in, and enclose the entire equation in double brackets, like this: [[a*b*c+d-e*f=125]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from bootcamp import Basebootcamp

def evaluate_expression(numbers, operators):
    nums = numbers.copy()
    ops = operators.copy()
    
    # 处理乘除运算
    i = 0
    while i < len(ops):
        if ops[i] in ('*', '/'):
            a = nums[i]
            b = nums[i+1]
            try:
                if ops[i] == '*':
                    res = a * b
                else:
                    res = a // b if b != 0 else 0
                nums[i] = res
                del nums[i+1]
                del ops[i]
            except:
                return None
        else:
            i += 1
    
    # 处理加减运算
    try:
        result = nums[0]
        for i in range(len(ops)):
            if ops[i] == '+':
                result += nums[i+1]
            else:
                result -= nums[i+1]
        return result
    except:
        return None

class KorPuzzleMathPathbootcamp(Basebootcamp):
    def __init__(self, max_ops=4, allow_division=True, min_target=-50, max_target=100):
        self.params = {
            'max_ops': max_ops,
            'allow_division': allow_division,
            'min_target': min_target,
            'max_target': max_target,
            'max_attempts': 100
        }
    
    def case_generator(self):
        allowed_ops = ['+', '-', '*']
        if self.params['allow_division']:
            allowed_ops.append('/')
        
        for _ in range(self.params['max_attempts']):
            n_ops = random.randint(1, self.params['max_ops'])
            ops = [random.choice(allowed_ops) for _ in range(n_ops)]
            num_vars = n_ops + 1
            numbers = []
            valid = True
            
            numbers.append(random.randint(0, 9))
            for i in range(n_ops):
                op = ops[i]
                if op == '/':
                    prev_num = numbers[i]
                    if prev_num == 0:
                        next_num = random.randint(1, 9)
                    else:
                        possible_divisors = [x for x in range(1, 10) if x != 0 and prev_num % x == 0]
                        if not possible_divisors:
                            valid = False
                            break
                        next_num = random.choice(possible_divisors)
                    numbers.append(next_num)
                else:
                    numbers.append(random.randint(0, 9))
            
            if not valid:
                continue
            
            target = evaluate_expression(numbers, ops)
            if target is None:
                continue
            if not (self.params['min_target'] <= target <= self.params['max_target']):
                continue
            
            return {
                'operators': ops,
                'target': target,
                'num_vars': num_vars
            }
        
        return {
            'operators': ['+', '*'],
            'target': 10,
            'num_vars': 3
        }
    
    @staticmethod
    def prompt_func(question_case):  # 修正此处缩进
        operators = question_case['operators']
        target = question_case['target']
        equation = '?'
        for op in operators:
            equation += f'{op}?'
        equation += f'={target}'
        
        prompt = f"""你是一位数学谜题解答专家，需要解决以下等式问题。请用0到9的数字填入问号，使等式成立。遵循数学中的运算顺序规则（先乘除，后加减）。

等式： {equation}

要求：
- 每个问号必须填入一个0到9之间的整数
- 允许重复使用数字
- 严格按照正确运算顺序计算结果

请提供一个可行的解，并将完整等式用双括号括起来，例如：[[答案填入这里]]。确保将最终答案放置在双括号内。"""
        return prompt
    
    @staticmethod  # 修正此处缩进
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1] if matches else None
    
    @classmethod  # 修正此处缩进
    def _verify_correction(cls, solution, identity):
        try:
            if '=' not in solution:
                return False
            left, right = solution.split('=', 1)
            target = int(right.strip())
            if target != identity['target']:
                return False
            
            tokens = re.findall(r'(\d+|\+|\-|\*|/)', left)
            if len(tokens) < 1 or len(tokens) % 2 == 0:
                return False
            
            numbers = []
            operators = []
            for i, token in enumerate(tokens):
                if i % 2 == 0:
                    if not token.isdigit():
                        return False
                    num = int(token)
                    if num < 0 or num > 9:
                        return False
                    numbers.append(num)
                else:
                    operators.append(token)
            
            if len(operators) != len(identity['operators']):
                return False
            for op_case, op_user in zip(identity['operators'], operators):
                if op_case != op_user:
                    return False
            
            calculated = evaluate_expression(numbers, operators)
            return calculated == identity['target']
        except:
            return False
