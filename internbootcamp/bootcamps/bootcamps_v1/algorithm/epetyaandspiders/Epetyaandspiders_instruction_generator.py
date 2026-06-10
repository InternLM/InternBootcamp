import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def get_bit(a, n):
    return (a >> n) & 1

def reset_bit(a, n):
    return a & ~(1 << n)

def calculate_max_empty(n, m):
    # Ensure n is the larger dimension for optimization
    if m > n:
        n, m = m, n
    if m == 0:
        return 0  # Should not happen for valid input
    max_size = 1 << m
    dp = [[[-1000] * max_size for _ in range(max_size)] for __ in range(n + 1)]
    initial_mask = (1 << m) - 1
    dp[0][0][initial_mask] = 0
    
    for i in range(1, n + 1):
        for prev_row in range(max_size):
            for prev_mask in range(max_size):
                if dp[i-1][prev_row][prev_mask] == -1000:
                    continue
                for current_row in range(max_size):
                    # Calculate spiders present in current configuration
                    combined = prev_row | current_row
                    cnt = sum(1 for bit in range(m) if not get_bit(combined, bit))
                    
                    # Calculate new_mask based on spider movements
                    new_mask = initial_mask
                    for bit in range(m):
                        if get_bit(combined, bit):
                            if m == 1:
                                new_mask = reset_bit(new_mask, 0)
                            else:
                                for offset in (-1, 0, 1):
                                    pos = bit + offset
                                    if 0 <= pos < m:
                                        new_mask = reset_bit(new_mask, pos)
                    
                    next_mask = new_mask & prev_mask
                    dp[i][next_mask][current_row] = max(
                        dp[i][next_mask][current_row], 
                        dp[i-1][prev_row][prev_mask] + cnt
                    )
    
    # Find maximum value in final state
    return max(dp[n][0][state] for state in range(max_size))


class EpetyaandspidersInstructionGenerator(BaseInstructionGenerator):
    """Epetyaandspiders Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Epetyaandspiders指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.params = params
        self.params.setdefault('n', None)
        self.params.setdefault('m', None)
    
    def case_generator(self):
        # Generate valid (n, m) pairs where 1 ≤ n,m ≤40 and n*m ≤40
        n = self.params['n']
        m = self.params['m']
        
        if n is None or m is None:
            possible = []
            for a in range(1, 41):
                for b in range(1, 41):
                    if a * b <= 40:
                        possible.append((a, b))
            if possible:
                n, m = random.choice(possible)
            else:
                n, m = 1, 1
        
        answer = calculate_max_empty(n, m)
        return {'n': n, 'm': m, 'answer': answer}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        return f"""You are a programming competition expert. Solve the following problem:

Petya has a board of size {n} rows × {m} columns. Each cell starts with a spider. All spiders simultaneously move to adjacent cells or stay in place for 1 second. Find the maximum number of empty cells possible after exactly one second.

Movement rules:
1. Epetyaandspiderss cannot move outside the board
2. Multiple spiders can occupy the same cell
3. Valid moves: stay (s), left (l), right (r), up (u), down (d)

Examples:
Input: 1 1 → Output: 0
Input: 2 3 → Output: 4

Your task: Given a {n}x{m} grid, compute the maximum possible empty cells after one second.

Format your answer as [answer]NUMBER[/answer]. Example: [answer]4[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

