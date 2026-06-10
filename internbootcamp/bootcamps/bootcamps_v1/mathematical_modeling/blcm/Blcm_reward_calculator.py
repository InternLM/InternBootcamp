import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import math




class BlcmRewardCalculator(BaseRewardCalculator):
    """Blcm奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强匹配模式，允许数值前后的空格
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        def count_factors(n):
            """优化后的因数计数器"""
            if n == 1:
                return 1
            total = 1
            # 预生成质数列表加速分解
            for p in cls._primes_up_to(math.isqrt(n) + 1):
                if p*p > n:
                    break
                exponent = 0
                while n % p == 0:
                    exponent += 1
                    n = n // p
                if exponent > 0:
                    total *= (exponent + 1)
            if n > 1:  # 剩余的大质数
                total *= 2
            return total
        
        return solution == count_factors(identity['b'])
    
    # 其他额外方法

