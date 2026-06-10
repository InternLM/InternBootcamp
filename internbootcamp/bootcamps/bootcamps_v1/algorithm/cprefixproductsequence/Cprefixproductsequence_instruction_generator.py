import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from math import isqrt




class CprefixproductsequenceInstructionGenerator(BaseInstructionGenerator):
    """Cprefixproductsequence Bootcamp指令生成器"""
    
    def __init__(self, max_n=1e5, **kwargs):
        """
        初始化Cprefixproductsequence指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = int(max_n)
    
    def case_generator(self):
        # Valid case candidates
        valid = {1, 4}
        primes = set(self.sieve())
        valid.update(primes)
        
        # Generate case type
        candidates = list(range(1, self.max_n+1))
        exist_cases = [n for n in candidates if n in valid]
        non_exist_cases = [n for n in candidates if n not in valid]
        
        # Ensure balanced case generation
        if exist_cases and (random.random() < 0.5 or not non_exist_cases):
            n = random.choice(exist_cases)
            return {'n': n, 'exists': True}
        elif non_exist_cases:
            return {'n': random.choice(non_exist_cases), 'exists': False}
        else:  # Fallback when all cases are valid
            return {'n': 1, 'exists': True}
    
    @staticmethod
    def prompt_func(case):
        n = case['n']
        return f"""Given n={n}, determine if there exists a permutation of 1-{n} where: 
1. All prefix products modulo {n} 
2. Form a permutation of 0-{n-1}

Output format (inside [answer] tags):
[answer]
YES
<p1>
<p2>
...
<p{n}>
[/answer]
OR
[answer]
NO
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def sieve(self):
        """Optimized sieve with bytearray storage"""
        if self.max_n < 2:
            return []
        sieve = bytearray([1])*(self.max_n+1)
        sieve[0] = sieve[1] = 0
        for i in range(2, isqrt(self.max_n)+1):
            if sieve[i]:
                sieve[i*i : self.max_n+1 : i] = b'\x00'*len(sieve[i*i : self.max_n+1 : i])
        return [i for i, v in enumerate(sieve) if v]
