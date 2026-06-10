import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CprimesonintervalRewardCalculator(BaseRewardCalculator):
    """Cprimesoninterval奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        def optimized_solver(a, b, k):
            if a > b or k == 0:
                return -1

            # 生成区间内的素数列表
            def generate_primes(low, high):
                if high < 2:
                    return []
                sieve = [True] * (high + 1)
                sieve[0] = sieve[1] = False
                for i in range(3, int(high**0.5)+1, 2):
                    if sieve[i]:
                        sieve[i*i::2*i] = [False] * len(sieve[i*i::2*i])
                
                primes = []
                if low <= 2 <= high:
                    primes.append(2)
                primes += [i for i in range(3, high+1, 2) if sieve[i] and i >= low]
                return primes

            primes = generate_primes(a, b)
            
            if len(primes) < k:
                return -1
            
            if k == 1:
                max_gap = max(
                    primes[0] - a + 1,
                    b - primes[-1] + 1,
                    max(p2 - p1 for p1, p2 in zip(primes, primes[1:]))
                )
                return max_gap
            
            if len(primes) == k:
                return max(primes[-1] - a + 1, b - primes[0] + 1)
            
            return max(
                primes[k-1] - a + 1,
                b - primes[-k] + 1,
                max(primes[i+k] - primes[i] for i in range(len(primes)-k))
            )

        try:
            a = identity['a']
            b = identity['b']
            k = identity['k']
            user_answer = int(solution)
            
            # 特殊情况处理
            if user_answer == -1:
                actual_primes = generate_primes(a, b)
                return len(actual_primes) < k
            
            # 计算正确答案
            correct_answer = optimized_solver(a, b, k)
            return user_answer == correct_answer
        except:
            return False
    
    # 其他额外方法

