import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DvasyaandchessInstructionGenerator(BaseInstructionGenerator):
    """Dvasyaandchess Bootcamp指令生成器"""
    
    def __init__(self, n=None, min_n=2, max_n=10**9, parity=None):
        """
        初始化Dvasyaandchess指令生成器
        
        Args:
            n: 参数描述
            min_n: 参数描述
            max_n: 参数描述
            parity: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.min_n = max(2, min_n)
        self.max_n = min(max_n, 10**9)
        self.parity = parity

        # Validate parameters on initialization
        if self.n is not None:
            if not (self.min_n <= self.n <= self.max_n):
                raise ValueError(f"n must be between {self.min_n} and {self.max_n}")
            if self.parity:
                actual_parity = 'even' if self.n % 2 == 0 else 'odd'
                if self.parity != actual_parity:
                    raise ValueError(f"Specified parity {self.parity} conflicts with fixed n={self.n}")
    
    def case_generator(self):
        if self.n is not None:
            return {'n': self.n}
        
        # 高效生成候选值算法
        def generate_candidate():
            if self.parity == 'even':
                start = self.min_n if self.min_n % 2 == 0 else self.min_n + 1
                end = self.max_n if self.max_n % 2 == 0 else self.max_n - 1
                if start > end:
                    raise ValueError("No even numbers in range")
                return random.randrange(start, end + 1, 2)
            
            elif self.parity == 'odd':
                start = self.min_n if self.min_n % 2 == 1 else self.min_n + 1
                end = self.max_n if self.max_n % 2 == 1 else self.max_n - 1
                if start > end:
                    raise ValueError("No odd numbers in range")
                return random.randrange(start, end + 1, 2)
            
            else:  # 无奇偶性要求
                return random.randint(self.min_n, self.max_n)
        
        try:
            n = generate_candidate()
            return {'n': n}
        except ValueError as e:
            raise ValueError(f"No valid n in range [{self.min_n}, {self.max_n}] with parity {self.parity}") from e
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        return f"""Vasya is playing a variant of chess on a {n}x{n} board. The white queen starts at (1,1), and the black queen at (1,{n}). All other cells contain green pawns. Players alternate turns, with white moving first. Each move must capture an enemy piece (green pawn or opposing queen) along a clear path. The player loses if unable to capture or if their queen was captured.

Given n = {n}, determine the winner with optimal play. If white wins, specify their first move's coordinates (smallest row then column).

Output your answer within [answer] tags. Examples:
[answer]white
1 2[/answer]
[answer]black[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

