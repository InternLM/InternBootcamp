import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
from collections import defaultdict

# === 源文件中的全局函数 ===

def calculate_answer(s, p):
    m = len(p)
    n = len(s)
    if m == 0 or n < m:
        return 0
    
    # Initialize frequency counter for p
    count_p = defaultdict(int)
    for c in p:
        count_p[c] += 1
    
    # Initialize sliding window parameters
    current_counts = defaultdict(int)
    required = len(count_p)
    formed = 0
    ans = 0
    q_count = 0  # number of '?' in current window
    
    left = 0
    for right in range(n):
        # Add right character
        char = s[right]
        if char == '?':
            q_count += 1
        else:
            current_counts[char] += 1
            if current_counts[char] == count_p.get(char, 0):
                formed += 1
        
        # Maintain window size m
        if right - left + 1 > m:
            # Remove left character
            left_char = s[left]
            if left_char == '?':
                q_count -= 1
            else:
                if current_counts[left_char] == count_p.get(left_char, 0):
                    formed -= 1
                current_counts[left_char] -= 1
            left += 1
        
        # Check window validity when window size is exactly m
        if right - left + 1 == m:
            # Calculate needed characters
            needed = sum(max(0, count_p[c] - current_counts[c]) for c in count_p)
            if needed <= q_count and formed == required:
                ans += 1
    
    return ans


class CanagramsearchInstructionGenerator(BaseInstructionGenerator):
    """Canagramsearch Bootcamp指令生成器"""
    
    def __init__(self, max_s_length=10, max_p_length=5, **kwargs):
        """
        初始化Canagramsearch指令生成器
        
        Args:
            max_s_length: 参数描述
            max_p_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_s_length = max_s_length
        self.max_p_length = max_p_length
    
    def case_generator(self):
        # Generate valid length combination
        m = random.randint(1, self.max_p_length)
        max_s_len = max(m + random.randint(-2,3), 1)  # allow s shorter than p
        s_len = random.randint(1, self.max_s_length)
        
        # Generate p with random letters
        p = ''.join(random.choices(string.ascii_lowercase, k=m))
        
        # Generate s with letters and ?'s
        s = []
        num_q = random.randint(0, min(s_len, 3))
        for _ in range(s_len):
            if random.random() < 0.3 and num_q > 0:
                s.append('?')
                num_q -= 1
            else:
                s.append(random.choice(string.ascii_lowercase))
        
        return {
            's': ''.join(s),
            'p': p,
            '_answer': calculate_answer(''.join(s), p)  # precompute answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""Given strings:
s = "{question_case['s']}" (with '?' wildcards)
p = "{question_case['p']}"

Count how many substrings of s (with length {len(question_case['p'])} if possible) can become anagrams of p after replacing '?'s. 

Output format: 
[answer]NUMBER[/answer]

Example: If answer is 5:
[answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

