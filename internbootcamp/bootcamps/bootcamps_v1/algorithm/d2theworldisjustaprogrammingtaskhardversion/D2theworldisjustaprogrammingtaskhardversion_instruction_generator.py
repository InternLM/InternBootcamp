import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class D2theworldisjustaprogrammingtaskhardversionInstructionGenerator(BaseInstructionGenerator):
    """D2theworldisjustaprogrammingtaskhardversion Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化D2theworldisjustaprogrammingtaskhardversion指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 10)
        self.seed = params.get('seed', None)
        if self.seed is not None:
            random.seed(self.seed)
    
    def case_generator(self):
        n = self.n
        s = self._generate_random_string(n)
        max_beauty = 0
        best_l = 1
        best_r = 1
        for l in range(1, n+1):
            for r in range(l, n+1):
                s_list = list(s)
                s_list[l-1], s_list[r-1] = s_list[r-1], s_list[l-1]
                current_beauty = self.compute_beauty(''.join(s_list))
                if current_beauty > max_beauty:
                    max_beauty = current_beauty
                    best_l = l
                    best_r = r
        return {
            'n': n,
            's': s,
            'correct_l': best_l,
            'correct_r': best_r,
            'max_beauty': max_beauty
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        return f"Given a bracket string of length {n}: {s}, find two positions to swap to maximize the beauty. Output the maximum beauty, followed by the positions (1-based) on the next line, within [answer] tags." 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_random_string(self, n):
        return ''.join(random.choice('()') for _ in range(n))

    @staticmethod
    def compute_beauty(s):
        n = len(s)
        if n == 0:
            return 0
        arr = [1 if c == '(' else -1 for c in s]
        total = sum(arr)
        if total != 0:
            return 0
        # Precompute the suffix sums
        suffix_sum = [0] * (n + 1)
        for i in range(n-1, -1, -1):
            suffix_sum[i] = suffix_sum[i+1] + arr[i]
        # Find the maximum suffix sum
        max_suffix = -float('inf')
        for i in range(n):
            if suffix_sum[i] > max_suffix:
                max_suffix = suffix_sum[i]
        # Compute the number of valid shifts
        count = 0
        for k in range(n):
            valid = True
            balance = 0
            for i in range(n):
                balance += arr[(k + i) % n]
                if balance < 0:
                    valid = False
                    break
            if valid and balance == 0:
                count += 1
        return count
