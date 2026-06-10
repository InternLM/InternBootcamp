import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Koroperationunicodeffe1InstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicodeffe1 Bootcamp指令生成器"""
    
    def __init__(self, finite_prob=0.7, interval_prob=0.2, special_prob=0.1, max_size=5, element_type='mixed', **kwargs):
        """
        初始化Koroperationunicodeffe1指令生成器
        
        Args:
            finite_prob: 参数描述
            interval_prob: 参数描述
            special_prob: 参数描述
            max_size: 参数描述
            element_type: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
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
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
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
