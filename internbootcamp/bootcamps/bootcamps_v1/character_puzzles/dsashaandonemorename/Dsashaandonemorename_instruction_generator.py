import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict

# === 源文件中的全局函数 ===

def generate_palindrome(min_length=1, max_length=50):
    """Generate palindrome with controlled diversity"""
    length = random.randint(min_length, max_length)
    
    # Ensure non-uniform characters for 90% cases
    if random.random() < 0.9:
        chars = []
        while len(chars) < (length + 1)//2:
            c = random.choice('abcdefghijklmnopqrstuvwxyz')
            if not chars or c != chars[-1]:
                chars.append(c)
        
        # Ensure palindrome structure
        return ''.join(chars + chars[:-1][::-1]) if length%2 else ''.join(chars + chars[::-1])
    
    # Generate uniform palindrome for 10% cases
    c = random.choice('abcdefghijklmnopqrstuvwxyz')
    return c * length

def solve_puzzle(s):
    n = len(s)
    if n <= 1:
        return "Impossible"
    
    # Frequency analysis
    freq = defaultdict(int)
    for c in s:
        freq[c] += 1
    
    # Case 1: All characters same
    if len(freq) == 1:
        return "Impossible"
    
    # Case 2: Check for special odd-length cases
    if n % 2 == 1:
        odd_count = sum(1 for cnt in freq.values() if cnt % 2 != 0)
        if odd_count == 1 and len(freq) == 2:
            return "Impossible"
    
    # Try single cut solutions
    original = list(s)
    for i in range(n//2):
        rotated = s[i+1:] + s[:i+1]
        if rotated != s and rotated == rotated[::-1]:
            return 1
    
    # Default case needs 2 cuts
    return 2


class DsashaandonemorenameInstructionGenerator(BaseInstructionGenerator):
    """Dsashaandonemorename Bootcamp指令生成器"""
    
    def __init__(self, min_length=3, max_length=50):
        """
        初始化Dsashaandonemorename指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        while True:
            s = generate_palindrome(self.min_length, self.max_length)
            answer = solve_puzzle(s)
            
            # Ensure case diversity
            if answer == 1 and random.random() < 0.7:  # Favor cases with k=1
                return {'s': s, 'expected_answer': answer}
            elif answer == 2 and random.random() < 0.3:
                return {'s': s, 'expected_answer': answer}
            elif answer == "Impossible":
                return {'s': s, 'expected_answer': answer}
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        return f"""You need to find the minimal number of cuts (k) required to rearrange the palindrome '{s}' into a different palindrome. Consider these rules:

1. Each cut must split the string into contiguous parts
2. Parts can be reordered but not reversed
3. Final string must be a different palindrome

Examples:
- 'nolon' → 2 cuts (split into no|l|on → onlno)
- 'otto' → 1 cut (tt|oo → toot)

Format your answer as: [answer]k[/answer] or [answer]Impossible[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

