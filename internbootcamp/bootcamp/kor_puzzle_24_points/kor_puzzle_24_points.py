"""### 谜题描述
1.Randomly select four numbers from 1-13, the numbers can have repetition.
2.Using the four basic operation symbols of addition (+), subtraction (-), multiplication (×), and division (÷).
3.Can also use parentheses to change the order of operations.
4.The result is equal to 24.
5.Each number must be used and can be used only once.Example questions are as follows:

<example 0>
The four randomly selected numbers are:
9 5 2 2.
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 0>

<example 1>
The four randomly selected numbers are:
9 8 7 6.
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 1>

<example 2>
The four randomly selected numbers are:
9 5 2 7.
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 2>

<example 3>
The four randomly selected numbers are:
5 7 7 2.
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 3>

<example 4>
The four randomly selected numbers are:
6 5 1 7.
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 4>

<example 5>
The four randomly selected numbers are:
1 5 4 9
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 5>

<example 6>
The four randomly selected numbers are:
7 8 3 8
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 6>

<example 7>
The four randomly selected numbers are:
2 3 1 3
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 7>

<example 8>
The four randomly selected numbers are:
1 3 7 10
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 8>

<example 9>
The four randomly selected numbers are:
8 2 8 2
Your answer should be in the form of a calculation expression, like this: a + b / c - d, giving one answer is sufficient.
Wrap your final answer in double square brackets, like this: [[a + b / c - d]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from bootcamp import Basebootcamp

class KorPuzzle24Pointsbootcamp(Basebootcamp):
    def __init__(self, min_num=1, max_num=13, allow_repeats=True):
        # 参数有效性校验
        if not allow_repeats and (max_num - min_num + 1) < 4:
            raise ValueError("When allow_repeats=False, min_num and max_num must span at least 4 numbers")
        
        self.min_num = min_num
        self.max_num = max_num
        self.allow_repeats = allow_repeats
    
    def case_generator(self):
        MAX_ATTEMPTS = 1000
        for _ in range(MAX_ATTEMPTS):
            # 根据参数生成不同特性的数字组合
            if self.allow_repeats:
                numbers = [random.randint(self.min_num, self.max_num) for _ in range(4)]
            else:
                numbers = random.sample(range(self.min_num, self.max_num+1), 4)
            
            if self._has_solution(numbers):
                return {'numbers': sorted(numbers)}  # 排序便于后续验证
            
        raise RuntimeError("Failed to generate valid case after maximum attempts")
    
    @staticmethod
    def prompt_func(question_case) -> str:
        nums = question_case['numbers']
        example = "9 5 2 7 -> (9 - 5) × (7 - 2)" if 9 in nums else "8 2 8 2 -> 8 × (2 + 2) - 8"
        return f"""
You are a 24-point puzzle solver. Using these numbers exactly once: {', '.join(map(str, nums))},
combine them with +, -, ×, ÷ and parentheses to make 24.

Rules:
1. Use each number exactly once
2. Standard order of operations applies
3. Final result must be exactly 24

Examples:
{example}

Put your final expression within double square brackets. Example: [[(a × b) + (c ÷ d)]]
"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            # 提取并验证数字使用
            input_nums = sorted(identity['numbers'])
            used_nums = sorted(map(int, re.findall(r'\b\d+\b', solution)))
            if input_nums != used_nums:
                return False
            
            # 数学表达式验证
            expr = solution.replace('×', '*').replace('÷', '/').replace(' ', '')
            return abs(eval(expr) - 24) < 1e-6
        except:
            return False
    
    @classmethod
    def _has_solution(cls, numbers):
        def dfs(nums):
            if len(nums) == 1:
                return abs(nums[0] - 24) < 1e-6
            for i, a in enumerate(nums):
                for j, b in enumerate(nums):
                    if i == j:
                        continue
                    remaining = [n for idx, n in enumerate(nums) if idx not in (i,j)]
                    for op in ['+', '-', '*', '/']:
                        if op == '/' and b == 0:
                            continue
                        try:
                            res = eval(f"{a}{op}{b}") 
                            if dfs(remaining + [res]):
                                return True
                        except ZeroDivisionError:
                            continue
            return False
        
        return dfs(numbers)
