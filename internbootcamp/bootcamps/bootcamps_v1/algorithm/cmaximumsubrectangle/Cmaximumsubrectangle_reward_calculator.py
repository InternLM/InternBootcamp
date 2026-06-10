import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_min_prefix_sums(arr):
    n = len(arr)
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i+1] = prefix[i] + arr[i]
    
    min_sums = [float('inf')] * (n + 1)
    for k in range(1, n+1):
        min_sum = min(prefix[i+k] - prefix[i] for i in range(n - k + 1))
        min_sums[k] = min_sum
    return min_sums

def calculate_max_area(n, m, a, b, x):
    min_a = calculate_min_prefix_sums(a)
    min_b = calculate_min_prefix_sums(b)
    
    max_area = 0
    for i in range(1, n+1):
        for j in range(1, m+1):
            if min_a[i] * min_b[j] <= x:
                max_area = max(max_area, i * j)
    return max_area


class CmaximumsubrectangleRewardCalculator(BaseRewardCalculator):
    """Cmaximumsubrectangle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[ANSWER\]\s*(\d+)\s*\[/ANSWER\]', output)
        try:
            return int(matches[-1]) if matches else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == calculate_max_area(
            identity['n'], identity['m'],
            identity['a'], identity['b'],
            identity['x']
        )
    
    # 其他额外方法

