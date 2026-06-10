import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Cehabanda2operationtaskInstructionGenerator(BaseInstructionGenerator):
    """Cehabanda2operationtask Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cehabanda2operationtask指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = params.get('max_n', 2000)
        self.a_min = params.get('a_min', 0)
        self.a_max = params.get('a_max', 10**5)
    
    def case_generator(self):
        n = random.randint(1, min(20, self.max_n))
        if random.random() < 0.5:
            # Generate strictly increasing array
            max_initial = self.a_max - (n-1)
            if max_initial < self.a_min:
                max_initial = self.a_min
            current = random.randint(self.a_min, max_initial)
            a = [current]
            for _ in range(n-1):
                current += 1
                a.append(current)
        else:
            # Generate random array with validation
            a = []
            for _ in range(n):
                a.append(random.randint(self.a_min, self.a_max))
            
            # Check for strict increasing
            is_increasing = True
            for i in range(n-1):
                if a[i] >= a[i+1]:
                    is_increasing = False
                    break
            
            # Handle edge case when n=1 or array accidentally becomes increasing
            if is_increasing and n >= 2:
                # Break the increasing property
                a[-1] = a[-2] - 1 if (a[-2] > 0) else a[-2] + 1
        
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        return f"""You are given an array of {n} integers. Your task is to make it strictly increasing in no more than {n+1} operations. 

Original array: {' '.join(map(str, a))}

Allowed operations:
1. "1 i x" - Add x to the first i elements (0 ≤ x ≤ 1e6, 1 ≤ i ≤ {n})
2. "2 i x" - Take modulo x of the first i elements (1 ≤ x ≤ 1e6, 1 ≤ i ≤ {n})

Output format:
- First line: number of operations m
- Next m lines: operations in the specified format

If the array is already strictly increasing, output 0.

Put your answer within [answer] and [/answer] tags. Example:
[answer]
2
1 2 5
2 3 10
[/answer]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

