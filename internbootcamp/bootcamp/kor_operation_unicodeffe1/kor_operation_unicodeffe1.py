"""### 谜题描述
A￡B=(A∪B)−(A∩B).Example questions are as follows:

<example 0>
A={1,2,3}, B={3,4,5}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]].
</example 0>

<example 1>
A={a,b,c}, B={c,d,e}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]].
</example 1>

<example 2>
A={1,2,3,4,5}, B={4,5,6,7,8}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]]
</example 2>

<example 3>
A={m,n}, B={n,o,p}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]]
</example 3>

<example 4>
A={1,3,5}, B={2,4,6}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]]
</example 4>

<example 5>
A={x,y,z}, B={w,x,z}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]]
</example 5>

<example 6>
A={p,q,r}, B={q,r,s}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]].
</example 6>

<example 7>
A={x∈R∣x>0}, B={x∈R∣x<1}.
Compute A￡B.
Use a set like {x∣x<1} to present the answer. Use '≤' for less than or equal to, and '≥' for greater than or equal to. Separate conditions with 'or' if there are multiple conditions.
Please wrap the answer in double square brackets, like this: [[you answer]].
</example 7>

<example 8>
A={x∣x is a real number}, B = {x∣x^2<1}.
Compute A￡B.
Use a set like {x∣x<1} to present the answer. Use '≤' for less than or equal to, and '≥' for greater than or equal to. Separate conditions with 'or' if there are multiple conditions.
Please wrap the answer in double square brackets, like this: [[you answer]].
</example 8>

<example 9>
A={x∣x is a natural number}, B = {x∣x is postive}.
Compute A￡B.
Please wrap the answer in double square brackets, like this: [[{the elements in the collection}]]
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from bootcamp import Basebootcamp

class KorOperationUnicodeffe1bootcamp(Basebootcamp):
    def __init__(self, finite_prob=0.7, interval_prob=0.2, special_prob=0.1, max_size=5, element_type='mixed', **kwargs):
        super().__init__()
        total = finite_prob + interval_prob + special_prob
        if total <= 0:
            total = 1.0
            finite_prob = 0.7
            interval_prob = 0.2
            special_prob = 0.1
        self.finite_prob = finite_prob / total
        self.interval_prob = interval_prob / total
        self.special_prob = special_prob / total
        self.max_size = max_size
        self.element_type = element_type

    def case_generator(self):
        rand_val = random.random()
        if rand_val < self.finite_prob:
            return self.generate_finite_case()
        elif rand_val < self.finite_prob + self.interval_prob:
            return self.generate_interval_case()
        else:
            return self.generate_special_case()

    def generate_finite_case(self):
        element_type = self.element_type
        if element_type == 'mixed':
            element_type = random.choice(['number', 'letter'])
        
        size_A = random.randint(2, self.max_size)
        size_B = random.randint(2, self.max_size)
        
        if element_type == 'number':
            elements = list(range(1, 21))
            A = sorted(random.sample(elements, size_A))
            B = sorted(random.sample(elements, size_B))
        else:
            letters = [chr(ord('a') + i) for i in range(26)]
            A = sorted(random.sample(letters, size_A))
            B = sorted(random.sample(letters, size_B))
        
        A_set = set(A)
        B_set = set(B)
        solution = sorted(list(A_set.symmetric_difference(B_set)))
        return {
            'type': 'finite',
            'A': A,
            'B': B,
            'solution': solution
        }

    def generate_interval_case(self):
        template = random.choice([1, 2, 3])
        if template == 1:  # 非重叠区间
            a = random.randint(-5, 3)
            b = a + random.randint(2, 4)
            while True:
                c = random.randint(b+1, b+3)
                if c > b: break
            A_desc = f'x > {a}'
            B_desc = f'x < {b}'
            solution = f'{{x | x ≤ {a} or x ≥ {b}}}'
        elif template == 2:  # 包含区间
            a = random.randint(2, 5)
            b = random.randint(-3, a-1)
            A_desc = f'x < {a}'
            B_desc = f'x > {b}'
            solution = f'{{x | x ≤ {b} or x ≥ {a}}}'
        else:  # 二次不等式
            c = random.randint(1, 3)
            A_desc = 'x is a real number'
            B_desc = f'x² < {c**2}'
            solution = f'{{x | x ≤ -{c} or x ≥ {c}}}'
        return {
            'type': 'interval',
            'A': A_desc,
            'B': B_desc,
            'solution': solution
        }

    def generate_special_case(self):
        case_type = random.choice([1, 2])
        if case_type == 1:  # 自然数 vs 正整数
            return {
                'type': 'special',
                'A': 'x is a natural number (including 0)',
                'B': 'x is a positive integer',
                'solution': '{0}'
            }
        else:  # 全体实数 vs 空集
            return {
                'type': 'special',
                'A': 'x is a real number',
                'B': 'x is an element of empty set',
                'solution': '{x | x ∈ ℝ}'
            }

    @staticmethod
    def prompt_func(question_case) -> str:
        case_type = question_case.get('type', 'finite')
        if case_type == 'finite':
            A_str = "{" + ", ".join(map(str, question_case['A'])) + "}"
            B_str = "{" + ", ".join(map(str, question_case['B'])) + "}"
            prompt = f"Given two finite sets:\nA = {A_str}\nB = {B_str}\n\nCompute the symmetric difference A£B.\nFormat: [[sorted, comma-separated elements]]"
        elif case_type == 'interval':
            prompt = (
                f"Given:\nA = {{{question_case['A']}}}\n"
                f"B = {{{question_case['B']}}}\n\n"
                "Compute A£B using inequalities with ≤/≥.\n"
                "Format: [[{{x | condition}}]]"
            )
        else:
            prompt = (
                f"Given:\nA = {{{question_case['A']}}}\n"
                f"B = {{{question_case['B']}}}\n\n"
                "Compute A£B considering mathematical definitions.\n"
                "Format: [[set_notation]]"
            )
        
        rules = (
            "Rules:\n"
            "1. A£B = (A∪B) - (A∩B)\n"
            "2. Use comma-separated sorted elements for finite sets\n"
            "3. Use '≤'/'≥' for inequalities\n"
            "4. Answer MUST be within double square brackets\n\n"
        )
        return rules + prompt

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        case_type = identity.get('type', 'finite')
        correct = identity['solution']

        def normalize(s):
            s = re.sub(r'\s+', '', s).lower()
            s = s.replace('< =', '≤').replace('>=', '≥')
            s = s.replace('=<', '≤').replace('=>', '≥')
            return s

        if case_type == 'finite':
            try:
                elements = re.findall(r'[^,{}\s]+', solution)
                parsed = {int(e) if e.isdigit() else e for e in elements}
                return parsed == set(correct)
            except:
                return False
        else:
            return normalize(solution) == normalize(str(correct))
