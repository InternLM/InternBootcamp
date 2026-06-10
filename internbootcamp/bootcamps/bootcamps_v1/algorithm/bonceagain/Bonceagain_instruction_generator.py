import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import Counter




class BonceagainInstructionGenerator(BaseInstructionGenerator):
    """Bonceagain Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=100, T_min=1, T_max=10**7, a_min=1, a_max=300):
        """
        初始化Bonceagain指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            T_min: 参数描述
            T_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 1)  # Ensure n >= 1
        self.n_max = n_max
        self.T_min = max(T_min, 1)  # Ensure T >= 1
        self.T_max = T_max
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        # Generate base array
        n = random.randint(self.n_min, self.n_max)
        T = random.choice([
            1,  # Edge case: minimal T
            2 * n,  # Boundary case
            random.randint(2 * n + 1, self.T_max),  # Large T case
            random.randint(self.T_min, self.T_max)  # General case
        ])
        
        # Generate array with element distribution
        if random.random() < 0.3:
            # Generate uniform array
            val = random.randint(self.a_min, self.a_max)
            a = [val] * n
        else:
            # Generate normal array ensuring max frequency cases
            a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
            if random.random() < 0.2:
                # Create a dominant element
                dominant = random.choice(a)
                a = [dominant if random.random() < 0.7 else x for x in a]
        
        return {'n': n, 'T': T, 'array': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        T = question_case['T']
        a = question_case['array']
        return f"""Find the length of the longest non-decreasing subsequence in a concatenated array.

Problem Statement:
- The base array [{', '.join(map(str, a))}] is repeated {T} times
- The subsequence can select elements from any position in the concatenated array
- Subsequence must maintain original order and be non-decreasing

Output Format:
Your answer should be a single integer enclosed in [answer][/answer] tags.

Example:
For input (n=4, T=3) with array [3, 1, 4, 2], the correct answer is:
[answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

