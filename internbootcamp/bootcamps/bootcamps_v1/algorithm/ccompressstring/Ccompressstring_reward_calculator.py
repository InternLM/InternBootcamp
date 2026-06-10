import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_min_coins(n, a_val, b_val, s):
    DP = [0] * (n + 1)
    for i in range(n):
        low = 0
        high = i + 1
        while low < high:
            mid = (low + high) // 2
            substring = s[mid:i+1]
            if substring in s[:mid]:
                high = mid
            else:
                low = mid + 1
        best_c = low
        if best_c == i + 1:
            cost_with_b = float('inf')
        else:
            cost_with_b = DP[best_c] + b_val
        cost_single = DP[i] + a_val
        DP[i+1] = min(cost_with_b, cost_single)
    return DP[n]


class CcompressstringRewardCalculator(BaseRewardCalculator):
    """Ccompressstring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
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
        return solution == identity['correct_answer']
    
    # 其他额外方法

