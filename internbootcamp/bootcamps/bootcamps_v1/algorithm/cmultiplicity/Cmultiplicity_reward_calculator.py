import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
from collections import defaultdict

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

factor_cache = FactorCache()



# === 源文件中的全局函数 ===

def compute_answer(n, a):
    """完全重构的动态规划解法"""
    dp = defaultdict(int)
    dp[0] = 1  # 初始状态：空序列
    total = 0
    
    for num in a:
        factors = sorted(factor_cache.get_factors(num), reverse=True)
        for f in factors:
            if f == 0:
                continue
            prev = f - 1
            if prev in dp:
                contribution = dp[prev]
                total = (total + contribution) % MOD
                dp[f] = (dp[f] + contribution) % MOD
                
    return total



# === 源文件中的其他类 ===

class FactorCache:
    """优化后的因数缓存机制"""
    def __init__(self):
        self.cache = defaultdict(set)
    
    def get_factors(self, n):
        if n not in self.cache:
            factors = set()
            if n > 0:
                max_factor = int(math.isqrt(n))
                step = 2 if n % 2 else 1
                for i in range(1, max_factor + 1, step):
                    if n % i == 0:
                        factors.add(i)
                        factors.add(n//i)
            self.cache[n] = factors
        return self.cache[n]


class CmultiplicityRewardCalculator(BaseRewardCalculator):
    """Cmultiplicity奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == identity['correct_answer']
        except (ValueError, KeyError):
            return False
    
    # 其他额外方法

