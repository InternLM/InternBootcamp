import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import isqrt




class E1squarefreedivisioneasyversionInstructionGenerator(BaseInstructionGenerator):
    """E1squarefreedivisioneasyversion Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化E1squarefreedivisioneasyversion指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_prime = 3162  # sqrt(10^7) ≈ 3162.27
        self.primes = self._generate_primes(self.max_prime)
        self.big_primes_cache = {}
    
    def case_generator(self):
        # 生成多样化的测试用例
        case_type = random.choice([1,2,3,4])
        n = random.randint(1, 20)
        
        if case_type == 1:  # 全平方数
            a = [random.randint(1, 30)**2 for _ in range(n)]
        elif case_type == 2:  # 含大质数
            a = [random.choice([9617497, 9999991, 32452843]) for _ in range(n)]
        elif case_type == 3:  # 混合类型
            a = [random.choice([p**2, p**3, p]) for p in random.choices(self.primes[-10:], k=n)]
        else:  # 随机正常案例
            a = [random.randint(1, 10**4) for _ in range(n)]
        
        # 确保至少一个非空案例
        a = a if n > 0 else [1]
        expected = self._calculate_min_segments(a)
        return {'n': len(a), 'k': 0, 'a': a, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case):
        return (
            "将数组划分为最少的连续段，使得每段内任意两数的乘积不是完全平方数。\n"
            f"输入：\n{question_case['n']} 0\n{' '.join(map(str, question_case['a']))}\n"
            "输出最小段数，答案置于[answer][/answer]中。"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_primes(self, max_limit):
        sieve = [True] * (max_limit + 1)
        sieve[0:2] = [False, False]
        for i in range(2, isqrt(max_limit) + 1):
            if sieve[i]:
                sieve[i*i::i] = [False] * len(sieve[i*i::i])
        return [i for i, prime in enumerate(sieve) if prime]

    def _get_square_signature(self, x):
        residual = 1
        for p in self.primes:
            if p*p > x:
                break
            exponent = 0
            while x % p == 0:
                exponent += 1
                x //= p
            if exponent % 2 != 0:
                residual *= p
        if x > 1:
            sqrt_x = isqrt(x)
            if sqrt_x * sqrt_x == x:
                return residual
            self.big_primes_cache[x] = residual * x  # 合并剩余大质数
            return self.big_primes_cache[x]
        return residual

    def _calculate_min_segments(self, a):
        seen = set()
        segments = 1
        for num in a:
            sig = self._get_square_signature(num)
            if sig in seen:
                seen = {sig}
                segments += 1
            else:
                seen.add(sig)
        return segments
