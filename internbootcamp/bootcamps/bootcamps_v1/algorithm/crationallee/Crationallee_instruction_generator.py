import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CrationalleeInstructionGenerator(BaseInstructionGenerator):
    """Crationallee Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=20, a_min=-10**9, a_max=10**9, **params):
        """
        初始化Crationallee指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.n_min = n_min
        self.n_max = n_max
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        k = random.randint(1, n)
        # Generate w array with sum n, each >=1
        weights = [1] * k
        remaining = n - k
        for _ in range(remaining):
            idx = random.randint(0, k-1)
            weights[idx] += 1
        # Generate a array with n integers
        a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        return {
            'n': n,
            'k': k,
            'a': a,
            'w': weights
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        a = ' '.join(map(str, question_case['a']))
        w = ' '.join(map(str, question_case['w']))
        problem = f"""Lee has {n} integers to distribute among his {k} friends. Each friend must receive exactly the specified number of integers. The happiness of a friend is the sum of the maximum and minimum integers they receive. Your task is to find the maximum possible total happiness.

Input for this case:
- First line: {n} {k}
- Second line: {a}
- Third line: {w}

Please compute the maximum sum of happiness and provide the numerical answer within [answer] tags. For example: [answer]123[/answer]."""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

