import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def generate_primes(a, b):
    """独立的素数生成函数用于验证"""
    if b < 2:
        return []
    sieve = [True] * (b + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(b**0.5)+1):
        if sieve[i]:
            sieve[i*i::i] = [False]*len(sieve[i*i::i])
    return [p for p in range(a, b+1) if sieve[p]]


class CprimesonintervalInstructionGenerator(BaseInstructionGenerator):
    """Cprimesoninterval Bootcamp指令生成器"""
    
    def __init__(self, a_min=1, a_max=10**6, b_max=10**6, k_max=10**6):
        """
        初始化Cprimesoninterval指令生成器
        
        Args:
            a_min: 参数描述
            a_max: 参数描述
            b_max: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.a_min = a_min
        self.a_max = min(a_max, b_max)  # 确保a_max <= b_max
        self.b_max = b_max
        self.k_max = k_max
    
    def case_generator(self):
        a = random.randint(self.a_min, self.a_max)
        b = random.randint(a, self.b_max)
        k = random.randint(1, self.k_max)
        return {'a': a, 'b': b, 'k': k}
    
    @staticmethod
    def prompt_func(question_case):
        a = question_case['a']
        b = question_case['b']
        k = question_case['k']
        prompt = f"""You are conducting a survey on prime numbers. A prime number is a positive integer greater than 1 with exactly two distinct divisors: 1 and itself.

Your task is to find the minimum length l such that EVERY consecutive sequence of l numbers between {a} and {b} (inclusive) contains at least {k} prime numbers. If no such l exists, output -1.

Examples:
Input: 2 4 2 → Output: 3 (Primes [2,3] need 3-length window)
Input: 6 13 1 → Output: 4 (Primes [7,11,13] need 4-length window)
Input: 1 4 3 → Output: -1 (Only 2 primes exist)

Rules:
1. l must be the smallest integer satisfying: for ALL x where a ≤ x ≤ b-l+1,
   the window [x, x+l-1] contains ≥k primes
2. If total primes in [a,b] < k → output -1

Format your answer as:
[answer]你的答案[/answer]"""

        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

