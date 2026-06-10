import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random




class CjzzhuandapplesInstructionGenerator(BaseInstructionGenerator):
    """Cjzzhuandapples Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=100):
        """
        初始化Cjzzhuandapples指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(1, n_min)
        self.n_max = n_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m_correct = self.compute_max_groups(n)
        return {'n': n, 'm_correct': m_correct}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        return f"""Jzzhu has {n} apples numbered 1-{n}. Group them into pairs where each pair's GCD >1. Find the maximum groups.

Output format:
m
a1 b1
...
am bm

Put your answer between [answer] and [/answer]. Example:

[answer]
2
6 3
2 4
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_groups(n):
        if n < 2:
            return 0
        used = [False] * (n + 1)
        primes = []

        # Efficient sieve to find primes up to n//2
        sieve_size = (n // 2) + 1
        sieve = [True] * sieve_size
        sieve[0] = sieve[1] = False
        for i in range(2, int(math.isqrt(sieve_size)) + 1):
            if sieve[i]:
                sieve[i*i::i] = [False] * len(sieve[i*i::i])

        # Collect primes in the order: odd primes first, then 2
        primes = [i for i in range(3, sieve_size, 2) if sieve[i]]
        if 2 <= sieve_size:
            primes.append(2)

        total_groups = 0
        for prime in primes:
            if prime > n // 2:
                continue

            # Collect multiples of prime
            multiples = []
            if not used[prime]:
                multiples.append(prime)
                used[prime] = True

            max_multiple = n // prime
            for multiplier in range(3, max_multiple + 1):
                num = prime * multiplier
                if not used[num]:
                    multiples.append(num)
                    used[num] = True

            # Handle odd count
            if len(multiples) % 2 != 0:
                candidate = prime * 2
                if candidate <= n and not used[candidate]:
                    multiples.append(candidate)
                    used[candidate] = True

            total_groups += len(multiples) // 2

        return total_groups
