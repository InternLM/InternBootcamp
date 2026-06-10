import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CsubsequencesInstructionGenerator(BaseInstructionGenerator):
    """Csubsequences Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Csubsequences指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.k = params.get('k', 2)
        super().__init__(**params)
    
    def case_generator(self):
        sequence = random.sample(range(1, self.n+1), self.n)
        return {
            'n': self.n,
            'k': self.k,
            'sequence': sequence,
            'correct_answer': self.calculate_solution(self.n, self.k, sequence)
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        seq = '\n'.join(map(str, question_case['sequence']))
        return f"""Given a sequence of {n} distinct integers, find the number of strictly increasing subsequences with exactly {k+1} elements. 

Input format:
First line contains n and k: {n} {k}
Following {n} lines contain the sequence: 
{seq}

Rules:
1. A subsequence must maintain original element order
2. Elements must be strictly increasing
3. Count all possible valid subsequences

Provide your final answer as an integer within [answer] and [/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def calculate_solution(cls, n, k, sequence):
        if k == 0:
            return n

        ft_list = [cls.FenwickTree(n) for _ in range(k+1)]
        result = 0

        for num in sequence:
            for j in range(1, k+1):
                if j == 1:
                    prev = ft_list[j-1].query(num-1)
                else:
                    prev = ft_list[j-1].query(num-1)

                if j == k:
                    result += prev
                ft_list[j].update(num, prev)
            ft_list[0].update(num, 1)

        return result
