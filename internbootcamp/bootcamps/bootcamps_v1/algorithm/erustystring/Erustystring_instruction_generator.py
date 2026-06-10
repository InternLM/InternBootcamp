import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class ErustystringInstructionGenerator(BaseInstructionGenerator):
    """Erustystring Bootcamp指令生成器"""
    
    def __init__(self, max_length=5, max_questions=3):
        """
        初始化Erustystring指令生成器
        
        Args:
            max_length: 参数描述
            max_questions: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_length = max_length
        self.max_questions = max_questions
    
    def case_generator(self):
        n = random.randint(1, self.max_length)
        pattern_type = random.choice(['all_v', 'all_k', 'alternating', 'random'])
        original = []
        if pattern_type == 'all_v':
            original = ['V'] * n
        elif pattern_type == 'all_k':
            original = ['K'] * n
        elif pattern_type == 'alternating':
            original = ['V' if i%2 == 0 else 'K' for i in range(n)]
        else:
            original = [random.choice(['V', 'K']) for _ in range(n)]
        
        num_q = random.randint(0, min(self.max_questions, n))
        q_indices = random.sample(range(n), k=num_q)
        s = original.copy()
        for i in q_indices:
            s[i] = '?'
        s_str = ''.join(s)
        
        correct_periods = self.calculate_possible_periods(s_str)
        correct_periods.sort()
        return {
            'n': n,
            's': s_str,
            'correct_periods': correct_periods
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        s = question_case['s']
        prompt = f"""You are a programming competition participant. Solve the following string period puzzle.

Problem Description:
A string's period is an integer d (1 ≤ d ≤ n) where for all positions i, characters at i and i+d are equal (where i+d < n). Determine all possible periods after replacing '?' with 'V' or 'K'.

Input:
- A string of length {n}: {s}

Output Format:
Two lines:
1. Number of valid periods
2. Sorted valid periods separated by spaces

Enclose your answer between [answer] and [/answer]. Example:
[answer]
3
2 3 4
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def calculate_possible_periods(self, s):
        n = len(s)
        valid_periods = []

        for d in range(1, n+1):
            valid = True
            for r in range(d):  # Check each residue group
                has_v = False
                has_k = False
                # Check all positions in this residue group
                for pos in range(r, n, d):
                    char = s[pos]
                    if char == 'V':
                        has_v = True
                    elif char == 'K':
                        has_k = True
                    # Conflict detected in this group
                    if has_v and has_k:
                        valid = False
                        break
                if not valid:
                    break
            if valid:
                valid_periods.append(d)

        return valid_periods
