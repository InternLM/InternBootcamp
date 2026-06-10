import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def get_bit(a, n):
    return (a >> n) & 1

def reset_bit(a, n):
    return a & ~(1 << n)

def calculate_max_empty(n, m):
    # Ensure n is the larger dimension for optimization
    if m > n:
        n, m = m, n
    if m == 0:
        return 0  # Should not happen for valid input
    max_size = 1 << m
    dp = [[[-1000] * max_size for _ in range(max_size)] for __ in range(n + 1)]
    initial_mask = (1 << m) - 1
    dp[0][0][initial_mask] = 0
    
    for i in range(1, n + 1):
        for prev_row in range(max_size):
            for prev_mask in range(max_size):
                if dp[i-1][prev_row][prev_mask] == -1000:
                    continue
                for current_row in range(max_size):
                    # Calculate spiders present in current configuration
                    combined = prev_row | current_row
                    cnt = sum(1 for bit in range(m) if not get_bit(combined, bit))
                    
                    # Calculate new_mask based on spider movements
                    new_mask = initial_mask
                    for bit in range(m):
                        if get_bit(combined, bit):
                            if m == 1:
                                new_mask = reset_bit(new_mask, 0)
                            else:
                                for offset in (-1, 0, 1):
                                    pos = bit + offset
                                    if 0 <= pos < m:
                                        new_mask = reset_bit(new_mask, pos)
                    
                    next_mask = new_mask & prev_mask
                    dp[i][next_mask][current_row] = max(
                        dp[i][next_mask][current_row], 
                        dp[i-1][prev_row][prev_mask] + cnt
                    )
    
    # Find maximum value in final state
    return max(dp[n][0][state] for state in range(max_size))


class EpetyaandspidersRewardCalculator(BaseRewardCalculator):
    """Epetyaandspiders奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1])
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

