import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def compute_min_swaps(n, s):
    a, b, c = [], [], []
    for i in range(n):
        char = s[i]
        if char == 'V':
            a.append(i)
        elif char == 'K':
            b.append(i)
        else:
            c.append(i)
    
    def count(arr, st, x):
        ret = 0
        i = st
        while i < len(arr) and arr[i] < x:
            ret += 1
            i += 1
        return ret
    
    dp = defaultdict(lambda: float('inf'))
    dp[(0, 0, 0, 0)] = 0
    
    for i in range(len(a)+1):
        for j in range(len(b)+1):
            for k in range(len(c)+1):
                for p in range(2):
                    current_key = (i, j, k, p)
                    current_val = dp[current_key]
                    if current_val == float('inf'):
                        continue
                    
                    # Place V
                    if i < len(a):
                        cost = count(a, i, a[i]) + count(b, j, a[i]) + count(c, k, a[i])
                        new_key = (i+1, j, k, 1)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place K (only if previous was not V)
                    if j < len(b) and p == 0:
                        cost = count(a, i, b[j]) + count(b, j, b[j]) + count(c, k, b[j])
                        new_key = (i, j+1, k, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place other characters
                    if k < len(c):
                        cost = count(a, i, c[k]) + count(b, j, c[k]) + count(c, k, c[k])
                        new_key = (i, j, k+1, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
    
    return min(dp[(len(a), len(b), len(c), 0)], dp[(len(a), len(b), len(c), 1)])


class EbearandcompanyRewardCalculator(BaseRewardCalculator):
    """Ebearandcompany奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 加强提取的鲁棒性，允许数字前后的空格
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

