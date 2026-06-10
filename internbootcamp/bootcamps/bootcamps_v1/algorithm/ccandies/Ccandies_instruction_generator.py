import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcandiesInstructionGenerator(BaseInstructionGenerator):
    """Ccandies Bootcamp指令生成器"""
    
    def __init__(self, max_n=16, max_q=3):
        """
        初始化Ccandies指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max(1, max_n)  # Ensure max_n ≥ 1
        self.max_q = max(1, max_q)  # Ensure max_q ≥ 1
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        s = [random.randint(0, 9) for _ in range(n)]
        
        # Precompute all valid query lengths (powers of two)
        possible_lengths = []
        current_length = 1
        while current_length <= n:
            possible_lengths.append(current_length)
            current_length <<= 1
        
        # Generate queries with valid ranges
        queries = []
        for _ in range(min(self.max_q, 10)):  # Limit query count
            if not possible_lengths:
                break
            length = random.choice(possible_lengths)
            max_l = n - length + 1
            if max_l < 1:
                continue  # Skip if no valid range for this length
            l = random.randint(1, max_l)
            r = l + length - 1
            queries.append({'l': l, 'r': r})
        
        return {
            'n': n,
            's': s,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        s = ' '.join(map(str, question_case['s']))
        q = len(question_case['queries'])
        queries = '\n'.join([f"{query['l']} {query['r']}" for query in question_case['queries']])
        
        return f"""You are given a sequence of digits and must answer queries about the number of candies obtained during a specific merging process. 

Input:
{n}
{s}
{q}
{queries}

Output each answer on a separate line within [answer] tags. Example:
[answer]
3
0
1
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_f(subarray):
        total_candies = 0
        current = subarray.copy()
        while len(current) > 1:
            new_level = []
            level_candies = 0
            for i in range(0, len(current), 2):
                pair_sum = current[i] + current[i+1]
                if pair_sum >= 10:
                    level_candies += 1
                new_level.append(pair_sum % 10)
            total_candies += level_candies
            current = new_level
        return total_candies
