import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from functools import reduce
from collections import Counter




class EnecklaceInstructionGenerator(BaseInstructionGenerator):
    """Enecklace Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Enecklace指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'min_n': 1,
            'max_n': 26,
            'min_ai': 1,
            'max_ai': 10,
            'max_total': 100000  # Increased default max_total
        }
        self.params.update(params)
    
    def case_generator(self):
        params = self.params
        min_n, max_n = params['min_n'], params['max_n']
        min_ai, max_ai = params['min_ai'], params['max_ai']
        max_total = params['max_total']

        n = random.randint(min_n, max_n)
        
        # Special case handling for single color
        if n == 1:
            count = random.randint(max(2, min_ai), min(max_ai, max_total))
            return {'n': 1, 'a': [count]}
        
        # Generate valid bead counts
        a = [min_ai] * n
        total = n * min_ai
        remaining = min(max_total - total, max_ai*n - total)
        
        # Distribute remaining beads
        while remaining > 0:
            idx = random.randint(0, n-1)
            available = min(max_ai - a[idx], remaining)
            if available <= 0:
                continue
            add = random.randint(0, available)
            a[idx] += add
            remaining -= add
            total += add
        
        # Ensure minimum total of 2
        if sum(a) < 2:
            a[-1] += 2 - sum(a)
        
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        return f"""Ivan wants to create the most beautiful necklace possible. The necklace is circular, and a cut is beautiful if the remaining chain is a palindrome. Using {n} colors (a-{chr(ord('a')+n-1)}) with counts {a}, find:

1. Maximum number of beautiful cuts
2. A valid necklace arrangement

Format your answer as:
[answer]
{{max_cuts}}
{{necklace}}
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _calculate_max_cuts(cls, n, a):
        # Implementation from reference solution
        if n == 1:
            return a[0]

        odd_count = sum(1 for x in a if x % 2)
        if odd_count > 1:
            return 0

        g = reduce(lambda x,y: cls._gcd(x,y), a)
        return g

    @staticmethod
    def _gcd(a, b):
        return a if b == 0 else Enecklacebootcamp._gcd(b, a % b)

    @classmethod
    def _check_bead_counts(cls, necklace, n, a):
        counts = Counter(necklace)
        expected = {chr(97+i): cnt for i, cnt in enumerate(a)}
        return counts == expected

    @staticmethod
    def _count_beautiful_cuts(necklace):
        return sum(1 for i in range(len(necklace)) 
                   if (necklace[i+1:]+necklace[:i+1]) == (necklace[i+1:]+necklace[:i+1])[::-1])
