import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, digits_str):
    if n == 0:
        return 0
    d = [int(c) for c in digits_str]
    if n == 1:
        return 1
    
    # Initialize comparison matrix
    comp = [[0]*(n+1) for _ in range(n)]
    
    for l in range(1, n):
        equal_count = 0
        for i in range(n - l):
            j = i + l
            if d[i] == d[j]:
                equal_count += 1
                if equal_count >= l:
                    equal_count = l - 1
            else:
                if d[i] < d[j]:
                    # Mark all positions in the equal prefix
                    start = i - equal_count
                    end = i + 1
                    for k in range(start, end):
                        if k >= 0 and j - equal_count + (k - start) < n:
                            comp[k][j - equal_count + (k - start) + 1] = 1
                equal_count = 0
    
    # Dynamic programming table
    dp = [[0]*(n+1) for _ in range(n+1)]
    for j in range(1, n+1):
        dp[j][j] = 1
    
    # Fill DP table
    for i in range(1, n):
        if d[i] == 0:
            continue
        prefix_sum = 0
        for l in range(1, n - i + 1):
            prefix_sum = (prefix_sum + dp[i][l-1]) % MOD
            if l <= i:
                compare_pos = i - l
                if compare_pos >= 0 and comp[compare_pos][i]:
                    dp[i+l][l] = (prefix_sum + dp[i][l]) % MOD
                else:
                    dp[i+l][l] = prefix_sum
            else:
                dp[i+l][l] = prefix_sum
    
    # Calculate final answer
    total = 0
    for l in range(1, n+1):
        total = (total + dp[n][l]) % MOD
    return total


class DnewyearandancientprophecyRewardCalculator(BaseRewardCalculator):
    """Dnewyearandancientprophecy奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](\d+)\[/answer\]', output, re.I)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

