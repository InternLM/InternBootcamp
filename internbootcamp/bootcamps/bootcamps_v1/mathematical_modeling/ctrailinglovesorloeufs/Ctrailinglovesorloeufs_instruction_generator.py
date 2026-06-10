import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import math




class CtrailinglovesorloeufsInstructionGenerator(BaseInstructionGenerator):
    """Ctrailinglovesorloeufs Bootcamp指令生成器"""
    
    def __init__(self, max_n=10**18, max_b=10**12):
        """
        初始化Ctrailinglovesorloeufs指令生成器
        
        Args:
            max_n: 参数描述
            max_b: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_b = max_b
        self.small_prime_set = set(self.small_primes)
        self.small_is_prime = [i in self.small_prime_set for i in range(38)]
    
    def case_generator(self):
        # Generate n with logarithmic distribution
        n = int(10**random.uniform(0, math.log10(self.max_n)))
        if n > self.max_n:
            n = self.max_n
        
        # Generate b with realistic distribution
        b = random.randint(2, min(self.max_b, 10**6))  # Balance between diversity and performance
        
        # Prime factorization with early termination
        prime_divisors = set()
        temp_b = b
        
        # Check small primes first
        for p in self.small_primes:
            if temp_b % p == 0:
                prime_divisors.add(p)
                while temp_b % p == 0:
                    temp_b //= p
            if temp_b == 1:
                break
        
        # Handle remaining factors
        if temp_b > 1:
            sqrt_b = int(math.isqrt(temp_b))
            for d in range(self.small_primes[-1] + 2, sqrt_b + 1, 2):
                if d > temp_b:
                    break
                if temp_b % d == 0 and self.is_prime(d):
                    prime_divisors.add(d)
                    while temp_b % d == 0:
                        temp_b //= d
                    sqrt_b = int(math.isqrt(temp_b))
                if temp_b == 1:
                    break
            
            if temp_b > 1 and self.is_prime(temp_b):
                prime_divisors.add(temp_b)
        
        # Handle base cases
        if not prime_divisors and self.is_prime(b):
            prime_divisors.add(b)
        
        # Calculate exponents
        factors = []
        for p in sorted(prime_divisors):
            cnt = 0
            tmp = b
            while tmp % p == 0:
                cnt += 1
                tmp //= p
            factors.append((p, cnt))
        
        return {'n': n, 'b': b, 'factors': factors}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        b = question_case['b']
        return f"""Calculate the number of trailing zeros in the base-{b} representation of {n}!.
Provide your answer in [answer]...[/answer] tags. Example: [answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def check_composite(self, n, s, d, a):
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            return False
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                return False
        return True

    def is_prime(self, n):
        if n < 2: return False
        if n < 38: return self.small_is_prime[n]

        # Check small primes first
        for p in self.small_primes:
            if n % p == 0:
                return n == p

        # Miller-Rabin test
        d = n - 1
        s = 0
        while d % 2 == 0:
            d //= 2
            s += 1

        for a in self.i64_witnesses:
            a %= n
            if a == 0:
                continue
            if self.check_composite(n, s, d, a):
                return False
        return True
