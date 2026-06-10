import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BsifidandstrangesubsequencesInstructionGenerator(BaseInstructionGenerator):
    """Bsifidandstrangesubsequences Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=20, element_min=-100, element_max=100, special_cases_ratio=0.3):
        """
        初始化Bsifidandstrangesubsequences指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            element_min: 参数描述
            element_max: 参数描述
            special_cases_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.element_min = element_min
        self.element_max = element_max
        self.special_cases_ratio = special_cases_ratio
    
    def case_generator(self):
        if random.random() < self.special_cases_ratio:
            return self._generate_special_case()
        
        n = random.randint(self.min_n, self.max_n)
        a = [random.randint(self.element_min, self.element_max) for _ in range(n)]
        expected = self._compute_expected(a)
        return {'a': a, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        return f"""You are solving a "strange subsequence" problem. 

**Formal Requirements:**
Find the maximum length of a subsequence where:
∀i < j, |a_i - a_j| ≥ MAX (the maximum in the subsequence)

**Key Insights:**
1. All non-positive elements can always be selected together
2. Can add at most one positive element (which must satisfy min_diff ≥ that value)

**Input Array (n = {len(a)}):**
{' '.join(map(str, a))}

**Output Format:**
A single integer in [answer]...[/answer] tags. Example: [answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_special_case(self):
        case_type = random.choice([
            'all_positive', 'all_negative', 'mixed_signs',
            'single_element', 'with_zero_edge'
        ])

        n = random.randint(self.min_n, self.max_n)

        if case_type == 'all_positive':
            a = [random.randint(1, self.element_max) for _ in range(n)]
        elif case_type == 'all_negative':
            a = [random.randint(self.element_min, -1) for _ in range(n)]
        elif case_type == 'mixed_signs':
            a = [random.choice([-1, 1]) * random.randint(0, self.element_max) 
                for _ in range(n)]
        elif case_type == 'single_element':
            a = [random.randint(self.element_min, self.element_max)]
        else:  # with_zero_edge
            a = [0] + sorted([random.randint(-10, 10) for _ in range(n-1)])

        expected = self._compute_expected(a)
        return {'a': a, 'expected': expected}

    @staticmethod
    def _compute_expected(a):
        a_sorted = sorted(a)
        n = len(a_sorted)

        if a_sorted[0] > 0:
            return 1

        min_diff = float('inf')
        for i in range(1, n):
            diff = a_sorted[i] - a_sorted[i-1]
            min_diff = min(min_diff, diff)
            if a_sorted[i] > 0:
                return i+1 if min_diff >= a_sorted[i] else i
        return n
