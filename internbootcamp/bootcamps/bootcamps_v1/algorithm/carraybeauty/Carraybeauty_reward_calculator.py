import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from itertools import combinations




class CarraybeautyRewardCalculator(BaseRewardCalculator):
    """Carraybeauty奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        n = identity['n']
        k = identity['k']
        a = identity['a']
        mod = 998244353
        total = 0
        for indices in combinations(range(n), k):
            elements = [a[i] for i in indices]
            min_diff = float('inf')
            for i in range(k-1):
                diff = elements[i+1] - elements[i]
                if diff < min_diff:
                    min_diff = diff
            total = (total + min_diff) % mod
        return solution % mod == total % mod
    
    # 其他额外方法

