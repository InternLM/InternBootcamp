import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import math
from collections import defaultdict




class CarpaandagamewithmojtabaRewardCalculator(BaseRewardCalculator):
    """Carpaandagamewithmojtaba奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE | re.DOTALL)
        if matches:
            ans = matches[-1].strip().lower()
            if ans in {'mojtaba', 'arpa'}:
                return ans.capitalize()
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        m = defaultdict(int)
        
        def factorize(x):
            factors = {}
            if x == 1:
                return factors
            while x % 2 == 0:
                factors[2] = factors.get(2, 0) + 1
                x //= 2
            i = 3
            while i * i <= x:
                while x % i == 0:
                    factors[i] = factors.get(i, 0) + 1
                    x //= i
                i += 2
            if x > 1:
                factors[x] = 1
            return factors
        
        for x in a:
            factors = factorize(x)
            for p, k in factors.items():
                m[p] |= 1 << (k - 1)
        
        dp = {}
        def mex(s):
            ans = 0
            while ans in s:
                ans += 1
            return ans
        
        def grundy(bit):
            if bit in dp:
                return dp[bit]
            if bit == 0:
                return 0
            lg = bit.bit_length() - 1
            s = set()
            for i in range(lg + 1):
                q = 0
                for j in range(lg + 1):
                    if bit & (1 << j):
                        if j < i:
                            q |= 1 << j
                        elif j > i:
                            new_pos = j - i - 1
                            if new_pos >= 0:
                                q |= 1 << new_pos
                s.add(grundy(q))
            dp[bit] = mex(s)
            return dp[bit]
        
        total_xor = 0
        for p in m:
            # 重置缓存确保不同质数独立计算
            dp.clear()
            total_xor ^= grundy(m[p])
        
        correct = 'Mojtaba' if total_xor != 0 else 'Arpa'
        return solution.strip().lower() == correct.lower()
    
    # 其他额外方法

