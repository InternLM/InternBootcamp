import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
from collections import Counter




class CkcompletewordInstructionGenerator(BaseInstructionGenerator):
    """Ckcompleteword Bootcamp指令生成器"""
    
    def __init__(self, max_k=5, max_m=5, **params):
        """
        初始化Ckcompleteword指令生成器
        
        Args:
            max_k: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_k = max_k
        self.max_m = max_m
    
    def case_generator(self):
        while True:
            # Generate valid k and n with k < n
            k = random.randint(1, self.max_k)
            m = random.randint(2, self.max_m)
            n = k * m
            if k < n:
                break
        
        # Generate valid k-complete base structure
        group_size = (k + 1) // 2
        base_chars = [random.choice(string.ascii_lowercase) for _ in range(group_size)]
        
        # Build minimal k-complete string
        s = []
        for i in range(n):
            mod = i % k
            if mod >= group_size:
                mod = k - mod - 1  # Mirror for palindrome
            s.append(base_chars[mod % group_size])
        
        # Add controlled noise
        max_noise = min(n, max(1, n // 4))
        noise_count = random.randint(0, max_noise)
        noise_indices = random.sample(range(n), k=noise_count)
        for idx in noise_indices:
            available_chars = [c for c in string.ascii_lowercase if c != s[idx]]
            if available_chars:
                s[idx] = random.choice(available_chars)
        
        return {'n': n, 'k': k, 's': ''.join(s)}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        s = question_case['s']
        return f"""Given a word s of length {n} and integer k = {k}, find the minimum number of character changes needed to make it k-complete. The word is: "{s}"

A k-complete word must:
1. Be a palindrome
2. Have a period of k

Put your final answer between [answer] and [/answer] tags. Example: [answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n, k, s):
        group_size = (k + 1) // 2
        groups = [Counter() for _ in range(group_size)]

        for i, c in enumerate(s):
            mod = i % k
            if mod >= group_size:
                mod = k - mod - 1
            groups[mod % group_size][c] += 1

        total = sum(max(ct.values(), default=0) for ct in groups)
        return n - total
