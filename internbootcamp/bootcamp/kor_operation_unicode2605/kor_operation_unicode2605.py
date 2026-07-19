"""### 谜题描述
a★b=\int_{a}^{b} 2x \, dxExample questions are as follows:

<example 0>
Compute 1★3.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
Compute 0★2.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
Compute -1★1.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
Compute 2★5.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
Compute -2★2.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
Compute 3★6.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
Compute 4★7.
Please ensure the answer is a single number and wrap it in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
If a★3=8, find a.
The answer may be negative, if so write it in a format such as '-5'.
If there is more than one answer, please separate them with 'or', e.g.[[1or2]].
Please wrap the final answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
If 0★b=b, find b.
The answer may be negative, if so write it in a format such as '-5'.
If there is more than one answer, please separate them with 'or', e.g.[[1or2]].
Please wrap the final answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
If a★5=21, find a.
The answer may be negative, if so write it in a format such as '-5'.
If there is more than one answer, please separate them with 'or', e.g.[[1or2]].
Please wrap the final answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random
import re
import ast

def find_integer_pairs(X):
    pairs = []
    for m in range(1, abs(X) + 1):
        if X % m != 0:
            continue
        n = X // m
        # 考虑正负因子对
        for m1, n1 in [(m, n), (-m, -n)]:
            # 确保 (n - m) 和 (n + m) 是偶数（即 a, b 是整数）
            if (n1 - m1) % 2 == 0 and (n1 + m1) % 2 == 0:
                a = (n1 - m1) // 2
                b = (n1 + m1) // 2
                pairs.append((a, b))
    # 去重 + 排序（按 b 增序）
    return sorted(set(pairs), key=lambda x: x[1])

class KorOperationUnicode2605bootcamp(Basebootcamp):
    def __init__(self, compute_prob=0.5, equation_type2_prob=0, min_val=-10, max_val=10):
        super().__init__()
        if not 0 <= compute_prob <= 1 or not 0 <= equation_type2_prob <= 1:
            raise ValueError("Probability parameters must be between 0 and 1")
        if min_val >= max_val:
            raise ValueError("min_val must be less than max_val")
        
        self.compute_prob = compute_prob
        self.equation_type2_prob = equation_type2_prob
        self.min_val = min_val
        self.max_val = max_val

    def case_generator(self):
        if random.random() < self.compute_prob:
            a = random.randint(self.min_val, self.max_val - 1)  # 确保b > a的情况
            b = random.randint(a + 1, self.max_val)
            return {
                "type": "compute",
                "a": a,
                "b": b,
                "expected": b**2 - a**2
            }
        else:
            if random.random() < self.equation_type2_prob:
                return {
                    "type": "equation_type2",
                    "expected": [0, 1]
                }
            else:
                result = random.randint(1, 20)  # 生成正整数结果
                return {
                    "type": "equation_type1",
                    # "solve_var": random.choice(['a', 'b'])
                    "result": result,
                    "expected": find_integer_pairs(result)
                }

    def _gen_equation_case(self, result):
        """生成方程的有效整数解"""
        factors = [i for i in range(1, result+1) if result % i == 0]
        pairs = [(d, result//d) for d in factors]
        valid_solutions = list({x for a, b in pairs for x in (a, -a, b, -b)})
        return sorted(valid_solutions)

    @staticmethod
    def prompt_func(question_case):
        integral_rule = (
            "The operation a★b is defined as the definite integral of 2x from a to b.\n"
            "Mathematically: a★b = ∫ₐᵇ 2x dx.\n\n"
        )
        
        if question_case['type'] == 'compute':
            problem = f"Compute {question_case['a']}★{question_case['b']}"
        elif question_case['type'] == 'equation_type1':
            problem = f"Find integer pair such that a★b = {question_case['result']}"
        elif question_case['type'] == 'equation_type2':
            problem = "Solve 0★b = b"
        else:
            raise ValueError("Invalid question type")
        
        format_instruction = (
            "\n\nPresent answer as integer(s) in [[ ]] brackets. "
            "For multiple pair answers use [[(a,b),(a,b),(a,b)]] format."
        )
        return integral_rule + problem + format_instruction

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        if not matches:
            return None  
        solutions = []
        try:
            # 替换 Unicode 负号为 ASCII 负号
            match = matches[-1].strip().replace('−', '-')
            if not match:
                return []
            # print('match: ', match)
            solutions=ast.literal_eval(match)
        except ValueError:
            raise ValueError("Invalid output format")
        return solutions or None

    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution and identity['expected']:
            return False
        expected = identity['expected']
        if identity['type'] == 'equation_type1':
            result = identity['result']
            ground_truth = set(find_integer_pairs(result))
            solution = set(list(solution))
            # print('ground_truth:', ground_truth)
            # print('solution:', solution)
            if ground_truth == solution:
                return True
            correct_rate = len(solution & ground_truth) / len(ground_truth)
            return  correct_rate if correct_rate > 0.6 else False
        else:
            return int(solution) == expected

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorOperationUnicode2605bootcamp
        bootcamp = KorOperationUnicode2605bootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case, '\n' ,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('提取到的答案：', bootcamp_cls.extract_output(input_answer), '\n')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break