import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EanniversaryRewardCalculator(BaseRewardCalculator):
    """Eanniversary奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if not last_match.isdigit():
            return None
        return int(last_match)
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        m = identity['m']
        l = identity['l']
        r = identity['r']
        k = identity['k']
        
        def find_max_d(l, r, k):
            low = 1
            high = r
            max_d = 0
            while low <= high:
                mid = (low + high) // 2
                count = (r // mid) - ((l - 1) // mid)
                if count >= k:
                    max_d = mid
                    low = mid + 1
                else:
                    high = mid - 1
            return max_d
        
        d = find_max_d(l, r, k)
        
        def fib(n, mod):
            a, b = 0, 1
            for _ in range(n):
                a, b = b, (a + b) % mod
            return a
        
        if d == 0:
            correct = 0
        else:
            # 计算 F(d) mod m
            # 由于 d 可能很大，使用迭代方法避免栈溢出
            correct = fib(d, m)
        
        return solution == correct
    
    # 其他额外方法

