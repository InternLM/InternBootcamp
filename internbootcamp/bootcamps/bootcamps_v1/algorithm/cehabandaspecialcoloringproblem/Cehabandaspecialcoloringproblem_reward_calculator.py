import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
from collections import defaultdict
from itertools import combinations
from math import gcd
import re




class CehabandaspecialcoloringproblemRewardCalculator(BaseRewardCalculator):
    """Cehabandaspecialcoloringproblem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        if len(solution) != n - 1:
            return False
        
        def count_primes(k):
            if k < 2:
                return 0
            sieve = [True] * (k + 1)
            sieve[0] = sieve[1] = False
            for i in range(2, int(math.sqrt(k)) + 1):
                if sieve[i]:
                    sieve[i*i : k+1 : i] = [False] * len(sieve[i*i : k+1 : i])
            return sum(sieve)
        primes_count = count_primes(n)
        
        max_color = max(solution) if solution else 0
        if max_color != primes_count:
            return False
        
        color_groups = defaultdict(list)
        for idx, color in enumerate(solution):
            i = idx + 2  # i is from 2 to n
            color_groups[color].append(i)
        
        for group in color_groups.values():
            for a, b in combinations(group, 2):
                if gcd(a, b) == 1:
                    return False
        return True
    
    # 其他额外方法

