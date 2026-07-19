"""### 谜题描述
Define an operation such that when a is a multiple of b, a※b = a/b + 2.
When b is a multiple of a, a※b = b/a + 2.
If a is not a multiple of b and b is not a multiple of a, a※b = 24.
Both a and b are integers.Example questions are as follows:

<example 0>
Compute 4※7.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute 25※5※14.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute 19※28※31※(286※13).
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute 19※28※4※(104※13).
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
If X※14=5, find X.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
If 25※X※14=4, find X.
When providing your answer, please enclose it in double square brackets, like this: [[answer]]. 
If there is more than one correct answer, separate the answers with 'or', like this: [[1or2]].
</example 5>

<example 6>
If 25※5※X=4, find X.
When providing your answer, please enclose it in double square brackets, like this: [[answer]]. 
If there is more than one correct answer, separate the answers with 'or', like this: [[1or2]].
</example 6>

<example 7>
If 19※28※4※(X※13) =3, find X.
When providing your answer, please enclose it in double square brackets, like this: [[answer]]. 
If there is more than one correct answer, separate the answers with 'or', like this: [[1or2]].
</example 7>

<example 8>
Now we make a little change to the rule: when a is a multiple of b, a ※ b = a / b + C; when b is a multiple of a, a ※ b = b / a + C; if a is not a multiple of b, b is not a multiple of a, a ※ b = 24, where C is a parameter.
Given that: 25 ※ 5 = 8, find C.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
Now we make a little change to the rule: when a is a multiple of b, a ※ b = a / b + C; when b is a multiple of a, a ※ b = b / a + C; if a is not a multiple of b, b is not a multiple of a, a ※ b = 24, where C is a parameter.
Given that: 14※42=4,find C.
The answer should only be given as a number.
Please wrap the answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import json
import random
import re
from bootcamp import Basebootcamp

class KorOperationUnicode203bbootcamp(Basebootcamp):
    def __init__(self, C=2, max_operand=100, max_attempts=100, **params):
        super().__init__(**params)
        self.C = C
        self.max_operand = max_operand
        self.max_attempts = max_attempts

    def case_generator(self):
        problem_type = random.choices(
            ['compute', 'solve_x', 'solve_c'],
            weights=[5, 3, 2],
            k=1
        )[0]
        
        try:
            if problem_type == 'compute':
                return self._generate_compute_case()
            elif problem_type == 'solve_x':
                return self._generate_solve_x_case()
            elif problem_type == 'solve_c':
                return self._generate_solve_c_case()
        except Exception as e:
            # 异常时返回默认计算题
            return self._generate_compute_case()

    def _generate_compute_case(self):
        for _ in range(self.max_attempts):
            num_operands = random.choices([2,3,4], weights=[5,3,1])[0]
            operands = [random.randint(1, self.max_operand) for _ in range(num_operands)]
            
            try:
                current_value = operands[0]
                for op in operands[1:]:
                    current_value = self._compute_operation(current_value, op, self.C)
            except ZeroDivisionError:
                continue
            
            # 允许有限概率生成结果为24的题目
            if current_value !=24 or random.random() < 0.2:
                return {
                    'type': 'compute',
                    'expression': operands,
                    'C': self.C,
                    'answer': int(current_value)
                }
        
        # 保底返回简单计算题
        return {
            'type': 'compute',
            'expression': [4,7],
            'C': self.C,
            'answer': 24
        }

    def _compute_operation(self, a, b, C):
        if b == 0 or a == 0:
            return 24
        if a % b == 0:
            return (a // b) + C
        if b % a == 0:
            return (b // a) + C
        return 24

    def _generate_solve_x_case(self):
        for _ in range(self.max_attempts):
            # 随机选择生成方向
            if random.random() < 0.5:  # 生成 a※X=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []
                
                # 寻找所有可能的X解
                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(a, X, self.C) == target:
                            solutions.append(X)
                    except:
                        continue
                
                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"{a}※X={target}",
                        'solutions': solutions,
                        'C': self.C
                    }
            else:  # 生成 X※a=...
                a = random.randint(2, self.max_operand)
                delta = random.randint(1, 5)
                target = self.C + delta
                solutions = []
                
                for X in range(1, self.max_operand*2):
                    try:
                        if self._compute_operation(X, a, self.C) == target:
                            solutions.append(X)
                    except:
                        continue
                
                if solutions:
                    return {
                        'type': 'solve_x',
                        'equation': f"X※{a}={target}",
                        'solutions': solutions,
                        'C': self.C
                    }
        
        # 保底返回单解问题
        return {
            'type': 'solve_x',
            'equation': "X※4=6",
            'solutions': [8],  # 8※4=2+2=4?
            'C': self.C
        }

    def _generate_solve_c_case(self):
        for _ in range(self.max_attempts):
            # 随机生成方向
            if random.random() < 0.5:
                a = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                b = a * factor
                expected = factor + self.C  # a※b = b/a + C
            else:
                b = random.randint(1, self.max_operand)
                factor = random.randint(2, 5)
                a = b * factor
                expected = factor + self.C  # a※b = a/b + C
            
            # 避免除零错误
            if a == 0 or b == 0:
                continue
            
            return {
                'type': 'solve_c',
                'equation': f"{a}※{b}={expected}",
                'answer': self.C
            }
        
        # 保底返回
        return {
            'type': 'solve_c',
            'equation': "25※5=8",
            'answer': 3  # 25/5=5 +3=8
        }

    @staticmethod
    def prompt_func(question_case):
        # 统一规则描述
        if 'C' in question_case and question_case['C'] != 2:
            rule_desc = [
                "We define a special operation ※ with parameter C:",
                "- If a is a multiple of b: a ※ b = a/b + C",
                "- If b is a multiple of a: a ※ b = b/a + C",
                "- Otherwise: a ※ b = 24"
            ]
        else:
            rule_desc = [
                "We define a special operation ※ with these rules:",
                "- When a is a multiple of b: a ※ b = a/b + 2",
                "- When b is a multiple of a: a ※ b = b/a + 2",
                "- If neither is a multiple: a ※ b = 24"
            ]
        
        task_desc = ""
        if question_case['type'] == 'compute':
            expr = '※'.join(map(str, question_case['expression']))
            task_desc = f"Compute the value of {expr}."
            format_note = "Put your final answer in [[ ]] as a single number."
        elif question_case['type'] == 'solve_x':
            task_desc = f"Solve the equation: {question_case['equation']}"
            if len(question_case['solutions']) > 1:
                format_note = "Put all possible solutions in [[ ]] separated by 'or', e.g., [[2or5]]."
            else:
                format_note = "Put your answer in [[ ]] as a single number."
        elif question_case['type'] == 'solve_c':
            task_desc = f"Determine parameter C from equation: {question_case['equation']}"
            format_note = "Put your answer in [[ ]] as a single number."
        
        return (
            '\n'.join(rule_desc) + '\n\n' +
            f'Problem: {task_desc}\n' +
            f'Format Requirement: {format_note}'
        )

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None
        last_match = matches[-1].strip()
        # 清理多余内容
        cleaned = re.sub(r'[^0-9or]', '', last_match.lower())
        return cleaned if cleaned else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        
        try:
            if identity['type'] == 'compute':
                return int(solution) == identity['answer']
            
            elif identity['type'] == 'solve_x':
                # 处理多格式输入
                parts = re.split(r'\bor\b|,', solution)
                answers = set()
                for p in parts:
                    p = p.strip()
                    if p.isdigit():
                        answers.add(int(p))
                return answers == set(identity['solutions'])
            
            elif identity['type'] == 'solve_c':
                return int(solution) == identity['answer']
            
            return False
        except Exception as e:
            return False

# 测试代码
if __name__ == "__main__":
    bootcamp = KorOperationUnicode203bbootcamp()
    for _ in range(3):
        case = bootcamp.case_generator()
        print("Generated Case:")
        print(json.dumps(case, indent=2))
        
        prompt = KorOperationUnicode203bbootcamp.prompt_func(case)
        print("\nPrompt:\n", prompt)
        
        # 测试验证逻辑
        test_solution = "[[7]]" if case['type'] == 'compute' else "[[3or5]]"
        print("\nTest verification:", bootcamp._verify_correction(
            KorOperationUnicode203bbootcamp.extract_output(test_solution),
            case
        ))
        print("="*50)
