"""### 谜题描述
a#b is the average of all even numbers between a and b (including a and b).Example questions are as follows:

<example 0>
Compute 3#7.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute 2#5.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute 4#6.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute 1#5.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
Compute 3#9.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
If X#6=5, find X.
The answer should only be given as a number.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
If 3#X=4, find X.
The answer should only be given as a number.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
If X#5=3, find X.
The answer should only be given as a number.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
If X#7=6, find X.
The answer should only be given as a number.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
If 3#X=6, find X.
The answer should only be given as a number.
If there is more than one answer, please separate them with 'or',e.g.[[1or2]].
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random
from numbers import Number
from typing import Union
from bootcamp import Basebootcamp

class KorOperationUnicode0023bootcamp(Basebootcamp):
    def __init__(self, compute_range=(0, 20), solve_range=(0, 30)):
        self.c_min, self.c_max = compute_range
        self.s_min, self.s_max = solve_range

    def case_generator(self) -> dict:
        """生成两种问题类型：计算类（60%）和方程求解类（40%）"""
        return random.choice([
            self._generate_compute_case,
            self._generate_solve_case
        ])()

    def _generate_compute_case(self) -> dict:
        """生成数值计算问题"""
        while True:
            a, b = sorted([random.randint(self.c_min, self.c_max) for _ in range(2)])
            if (a + b) == 0:
                continue  # 避免除零错误
            
            even_numbers = [x for x in range(a, b+1) if x%2 == 0]
            if not even_numbers:
                continue
                
            avg = sum(even_numbers)/len(even_numbers)
            return {
                'type': 'compute',
                'params': {'a': a, 'b': b},
                'answer': avg
            }

    def _generate_solve_case(self) -> dict:
        """生成方程求解问题"""
        problem_type = random.choice(['solve_left', 'solve_right'])
        return {
            'solve_left': self._generate_left_solve_case,
            'solve_right': self._generate_right_solve_case
        }[problem_type]()

    def _generate_left_solve_case(self) -> dict:
        """生成X#b = target类型问题"""
        while True:
            # 生成合法区间
            b = random.randint(self.s_min, self.s_max)
            valid_x = []
            
            # 遍历所有可能的X值
            for x in range(self.s_min, b+1):
                # 计算x到b闭区间的偶数平均值
                evens = [n for n in range(min(x,b), max(x,b)+1) if n%2 ==0]
                if not evens:
                    continue
                avg = sum(evens)/len(evens)
                valid_x.append( (x, avg) )
            
            if not valid_x:
                continue
            
            # 选择有解的target值
            target_entry = random.choice(valid_x)
            target = target_entry[1]
            
            # 验证所有可能解
            solutions = []
            for x, avg in valid_x:
                if abs(avg - target) < 1e-9:
                    solutions.append(x)
            
            if solutions:
                return {
                    'type': 'solve_left',
                    'params': {'b': b, 'target': target},
                    'answer': solutions
                }

    def _generate_right_solve_case(self) -> dict:
        """生成a#X = target类型问题"""
        while True:
            a = random.randint(self.s_min, self.s_max)
            valid_x = []
            
            for x in range(a, self.s_max+1):
                evens = [n for n in range(min(a,x), max(a,x)+1) if n%2 ==0]
                if not evens:
                    continue
                avg = sum(evens)/len(evens)
                valid_x.append( (x, avg) )
            
            if not valid_x:
                continue
                
            target_entry = random.choice(valid_x)
            target = target_entry[1]
            
            solutions = []
            for x, avg in valid_x:
                if abs(avg - target) < 1e-9:
                    solutions.append(x)
            
            if solutions:
                return {
                    'type': 'solve_right',
                    'params': {'a': a, 'target': target},
                    'answer': solutions
                }

    @staticmethod
    def prompt_func(case: dict) -> str:
        """生成自然语言问题描述"""
        definition = "Define that a#b is the average of all even numbers between a and b (including a and b).\n\n"
        if case['type'] == 'compute':
            a = case['params']['a']
            b = case['params']['b']
            return definition + f"Compute {a}#{b}. All even numbers between (and including) {a} and {b} are considered.\nAnswer must be in [[answer]] format."
        
        elif case['type'].startswith('solve'):
            params = case['params']
            target = case['answer']
            
            # 格式化target显示
            target_value = params['target']
            if isinstance(target_value, float) and target_value.is_integer():
                target_value = int(target_value)
            
            if case['type'] == 'solve_left':
                return definition + f"If X#{params['b']} = {target_value}, find X. "\
                       f"Multiple answers should be separated by 'or'. "\
                       f"Put your answer in [[X]] or [[X1orX2]] format."
            else:
                return definition + f"If {params['a']}#X = {target_value}, find X. "\
                       f"Multiple answers should be separated by 'or'. "\
                       f"Put your answer in [[X]] or [[X1orX2]] format."

    @staticmethod
    def extract_output(text: str) -> Union[str, None]:
        """从回答文本中提取最后一个[[...]]内容"""
        matches = re.findall(r'\[\[(.*?)\]\]', text)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution: str, case: dict) -> bool:
        """验证答案正确性"""
        try:
            if case['type'] == 'compute':
                user_ans = float(solution)
                return abs(user_ans - case['answer']) < 1e-9
            
            else:  # 方程求解类型
                if 'or' in solution:
                    user_answers = set(map(int, solution.split('or')))
                else:
                    user_answers = {int(solution)}
                
                # 处理边界情况：允许answer字段存储为列表或数值
                correct_answers = set(case['answer'] if isinstance(case['answer'], list) else [case['answer']])
                return user_answers == correct_answers
                
        except (ValueError, TypeError):
            return False
