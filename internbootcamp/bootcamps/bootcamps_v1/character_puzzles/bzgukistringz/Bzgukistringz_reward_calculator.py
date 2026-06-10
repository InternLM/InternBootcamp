import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import Counter
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_max_counts(a, b, c):
    a_counts = [0] * 26
    for char in a:
        a_counts[ord(char) - ord('a')] += 1

    b_counts = [0] * 26
    for char in b:
        b_counts[ord(char) - ord('a')] += 1

    c_counts = [0] * 26
    for char in c:
        c_counts[ord(char) - ord('a')] += 1

    best_bs = 0
    best_cs = 0
    max_total = 0

    # 模拟原题代码，枚举bs到a的长度+1
    max_bs = len(a)
    for bs in range(0, max_bs + 1):
        possible = True
        a_clone = a_counts.copy()
        for i in range(26):
            required = bs * b_counts[i]
            if a_clone[i] < required:
                possible = False
                break
            a_clone[i] -= required
        if not possible:
            continue

        # 计算c的最大次数
        cs = float('inf')
        for i in range(26):
            if c_counts[i] == 0:
                continue
            available = a_clone[i]
            if available < c_counts[i]:
                cs = 0
                break
            cs = min(cs, available // c_counts[i])
        if cs == float('inf'):
            cs = 0

        total = bs + cs
        if total > max_total or (total == max_total and cs > best_cs):
            max_total = total
            best_bs = bs
            best_cs = cs

    return best_bs, best_cs

def count_max_substrings(k_str, b, c):
    subs = []
    len_b, len_c = len(b), len(c)
    if len_b > 0:
        subs.append((len_b, b))
    if len_c > 0 and b != c:
        subs.append((len_c, c))

    n = len(k_str)
    dp = [0] * (n + 1)

    for i in range(n):
        dp[i + 1] = max(dp[i + 1], dp[i])
        for length, sub in subs:
            if i + length > n:
                continue
            if k_str[i:i + length] == sub:
                dp[i + length] = max(dp[i + length], dp[i] + 1)
    return dp[n]


class BzgukistringzRewardCalculator(BaseRewardCalculator):
    """Bzgukistringz奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 检查solution是否是a的正确排列
        if Counter(solution) != Counter(identity['a']):
            return False
        
        # 计算最大非重叠子串数目
        calculated = count_max_substrings(solution, identity['b'], identity['c'])
        return calculated == identity['max_total']
    
    # 其他额外方法

