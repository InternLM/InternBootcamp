import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpalindrometransformationInstructionGenerator(BaseInstructionGenerator):
    """Cpalindrometransformation Bootcamp指令生成器"""
    
    def __init__(self, n=8, modification_prob=0.3):
        """
        初始化Cpalindrometransformation指令生成器
        
        Args:
            n: 参数描述
            modification_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = n
        self.modification_prob = modification_prob
    
    def case_generator(self):
        n = self.n
        # Generate initial palindrome
        half = [random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(n//2)]
        s = half + ([half[-1]] if n%2 else []) + half[::-1]
        s = s[:n]  # Ensure correct length for odd n
        
        sum_updown = 0
        modify_pairs = []
        original_pairs = []  # Track original characters
        
        for i in range(n//2):
            original_pairs.append((s[i], s[~i]))
            if random.random() < self.modification_prob:
                # Corrupt the palindrome
                delta = random.randint(1, 12)
                if random.choice([True, False]):
                    new_char = chr((ord(s[i]) - ord('a') + delta) % 26 + ord('a'))
                else:
                    new_char = chr((ord(s[i]) - ord('a') - delta) % 26 + ord('a'))
                s[i] = new_char
                
                # Calculate updown cost
                a, b = ord(new_char), ord(original_pairs[i][1])
                diff = abs(a - b)
                sum_updown += min(diff, 26 - diff)
                modify_pairs.append(i)
        
        # Calculate cursor position
        p = random.randint(1, n)
        adjusted_p = (n - p) if p > n//2 else (p - 1)
        
        # Handle no modification case
        l = min(modify_pairs) if modify_pairs else 0
        r = max(modify_pairs) if modify_pairs else 0
        
        return {
            'n': n,
            'p': p,
            's': ''.join(s),
            'sum_updown': sum_updown,
            'left': l,
            'right': r,
            'adjusted_p': adjusted_p
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Transform the string into a palindrome with minimal arrow presses.
Input:
{question_case['n']} {question_case['p']}
{question_case['s']}

Rules:
1. Cursor moves cyclically (left/right)
2. Up/Down change character cyclically
3. Initial cursor position: {question_case['p']}

Provide the minimal presses in [answer]...[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

