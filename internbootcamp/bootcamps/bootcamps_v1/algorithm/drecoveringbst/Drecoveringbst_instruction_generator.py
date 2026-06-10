import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import math
import random
from math import gcd
from collections import defaultdict




class DrecoveringbstInstructionGenerator(BaseInstructionGenerator):
    """Drecoveringbst Bootcamp指令生成器"""
    
    def __init__(self, n_min=3, n_max=15, yes_ratio=0.5, max_attempts=100):
        """
        初始化Drecoveringbst指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            yes_ratio: 参数描述
            max_attempts: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 2)
        self.n_max = min(n_max, 100)  # 控制最大规模
        self.yes_ratio = yes_ratio
        self.max_attempts = max_attempts
        self.prime_pool = self._sieve(200)  # 预备质数库
    
    def case_generator(self):
        for _ in range(self.max_attempts):
            generate_yes = random.random() < self.yes_ratio
            
            if generate_yes:
                # Yes案例：构建保证有解的树结构
                case = self._generate_yes_case()
                if case:
                    return case
            else:
                # No案例：确保无解的构造
                case = self._generate_no_case()
                if case:
                    return case
        
        # 生成失败时返回标准案例
        return {
            'n': 2,
            'array': [2, 3],
            'expected_answer': 'No' if gcd(2,3)==1 else 'Yes'
        }
    
    @staticmethod
    def prompt_func(question_case):
        elements = ' '.join(map(str, question_case['array']))
        return f"""Determine if a valid BST can be built from these sorted values where adjacent nodes have GCD>1.

Input:
{question_case['n']}
{elements}

Output format: [answer]Yes/No[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _sieve(self, n):
        sieve = [True] * (n+1)
        sieve[0:2] = [False]*2
        for i in range(2, int(n**0.5)+1):
            if sieve[i]:
                sieve[i*i::i] = [False]*len(sieve[i*i::i])
        return [i for i, b in enumerate(sieve) if b]

    def _generate_yes_case(self):
        """生成保证有解的案例：通过链式结构构造"""
        # 方法一：构建链式树（完全左/右子树）
        n = random.randint(self.n_min, self.n_max)
        base = random.choice([2, 3, 4, 5, 6])
        step = random.choice([2, 3, 4])
        arr = sorted([base * (step**i) for i in range(n)])

        # 方法二：共享因子的随机组合
        factors = random.sample(self.prime_pool, 3)
        candidates = []
        for _ in range(2*n):
            p = random.choice(factors)
            q = random.choice(factors)
            if p != q:
                candidates.append(p*q)
        arr = sorted(list(set(candidates)))[:n]
        if len(arr) < self.n_min:
            return None

        expected = self.check_possible(arr)
        if expected == 'Yes':
            return {
                'n': len(arr),
                'array': arr,
                'expected_answer': expected
            }
        return None

    def _generate_no_case(self):
        """生成保证无解的案例：互质数或特殊结构"""
        # 方法一：使用互质数
        primes = random.sample(self.prime_pool, self.n_max*2)
        arr = sorted(primes[:random.randint(self.n_min, self.n_max)])
        if all(math.gcd(a,b)==1 for a in arr for b in arr if a!=b):
            return {
                'n': len(arr),
                'array': arr,
                'expected_answer': 'No'
            }

        # 方法二：构造无法形成BST结构的案例
        while True:
            base = random.choice([2,3])
            arr = sorted([base**i for i in range(1, self.n_max+1)])
            if self.check_possible(arr) == 'No':
                return {
                    'n': len(arr),
                    'array': arr,
                    'expected_answer': 'No'
                }
            break

        return None

    @staticmethod
    def check_possible(a):
        # 优化后的验证算法（带记忆化）
        n = len(a)
        gcd_cache = [[math.gcd(a[i], a[j]) > 1 for j in range(n)] for i in range(n)]
        parent = [[-1]*n for _ in range(n)]
        dp = [[False]*n for _ in range(n)]

        # 构建根节点可能性
        for i in range(n):
            dp[i][i] = True

        # 区间DP
        for l in range(2, n+1):
            for i in range(n - l + 1):
                j = i + l - 1
                for k in range(i, j+1):
                    left_ok = (k == i) or (dp[i][k-1] and gcd_cache[k][k-1])
                    right_ok = (k == j) or (dp[k+1][j] and gcd_cache[k][k+1])
                    if left_ok and right_ok:
                        dp[i][j] = True
                        parent[i][j] = k
                        break

        return 'Yes' if dp[0][n-1] else 'No'
