import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re
from collections import Counter




class CphoenixanddistributionInstructionGenerator(BaseInstructionGenerator):
    """Cphoenixanddistribution Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cphoenixanddistribution指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.params = params
        self.min_length = params.get('min_length', 1)
        self.max_length = params.get('max_length', 20)
        self.force_diverse_cases = params.get('force_diverse_cases', False)
    
    def case_generator(self):
        if self.force_diverse_cases and random.random() < 0.5:
            return self._generate_edge_case()
        return self._generate_random_case()
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        s = question_case['s']
        problem = (
            f"## 字符串优化分配问题\n\n"
            f"给定字符串 s = '{s}'\n"
            f"需要分成 k = {k} 个非空子串\n\n"
            "### 规则说明\n"
            "1. 必须使用全部字符\n2. 允许重新排列每个子串\n3. 找到使最大子串字典序最小的方案\n\n"
            "请将最终答案放在[answer]和[/answer]标签之间，例如：[answer]abc[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_random_case(self):
        n = random.randint(self.min_length, self.max_length)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        k = random.randint(1, max(1, n//2)) if n > 1 else 1
        return {'n': n, 'k': k, 's': s}

    def _generate_edge_case(self):
        case_type = random.choice([1, 2, 3, 4])

        if case_type == 1:  # k=1的特殊情况
            s = ''.join(sorted(random.choices(string.ascii_lowercase, k=random.randint(5, 10))))
            return {'n': len(s), 'k': 1, 's': s}

        elif case_type == 2:  # 所有字符相同的情况
            char = random.choice(string.ascii_lowercase)
            n = random.randint(5, 15)
            k = random.randint(1, n)
            return {'n': n, 'k': k, 's': char * n}

        elif case_type == 3:  # 需要均匀分配的情况
            base_char = random.choice(string.ascii_lowercase)
            other_char = chr(ord(base_char) + 1)
            s = base_char * 5 + other_char * 10
            k = random.randint(3, 5)
            return {'n': len(s), 'k': k, 's': ''.join(random.sample(s, len(s)))}

        else:  # 首字符不满足k需求的情况
            first_char = 'a'
            rest_chars = ''.join(random.choices(string.ascii_lowercase[1:], k=random.randint(8, 15)))
            s = first_char * 3 + rest_chars
            k = 5  # 大于首字符数量(3)
            return {'n': len(s), 'k': k, 's': ''.join(random.sample(s, len(s)))}

    @classmethod
    def compute_correct_answer(cls, s, k):
        sorted_s = ''.join(sorted(s))
        n = len(sorted_s)
        first_char_count = sorted_s.count(sorted_s[0])

        if first_char_count < k or n == k:
            return sorted_s[k-1]
        else:
            if sorted_s[k] != sorted_s[-1]:
                return sorted_s[0] + sorted_s[k:]
            else:
                repeat = (n - 1) // k
                return sorted_s[0] + sorted_s[-1] * repeat

    @staticmethod
    def split_into_parts(sorted_s, k):
        # 辅助方法用于验证分割逻辑
        parts = []
        if Counter(sorted_s) == Counter(sorted_s[0]*len(sorted_s)):
            base = sorted_s[0]
            per_part = len(sorted_s) // k
            remainder = len(sorted_s) % k
            for i in range(k):
                parts.append(base * (per_part + (1 if i < remainder else 0)))
        else:
            parts = [sorted_s[0]] * k
            remaining = sorted_s[k:]
            for i in range(len(remaining)):
                parts[i % k] += remaining[i]
            parts = [''.join(sorted(p)) for p in parts]
        return parts
