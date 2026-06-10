import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, l, r):
    mod = 10**9 + 7

    def count_mod(low, high, m):
        remainder = low % 3
        if remainder <= m:
            first = low + (m - remainder)
        else:
            first = low + (3 - remainder + m)
        if first > high:
            return 0
        last = high - ((high - m) % 3)
        return ((last - first) // 3) + 1

    count0 = count_mod(l, r, 0)
    count1 = count_mod(l, r, 1)
    count2 = count_mod(l, r, 2)
    counts = [count0, count1, count2]

    # Dynamic programming approach
    dp_prev = counts.copy()
    for _ in range(n - 1):
        dp_next = [0] * 3
        for prev_mod in range(3):
            for curr_mod in range(3):
                new_mod = (prev_mod + curr_mod) % 3
                dp_next[new_mod] = (dp_next[new_mod] + dp_prev[prev_mod] * counts[curr_mod]) % mod
        dp_prev = dp_next

    return dp_prev[0] % mod


class CayoubandlostarrayRewardCalculator(BaseRewardCalculator):
    """Cayoubandlostarray奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
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

