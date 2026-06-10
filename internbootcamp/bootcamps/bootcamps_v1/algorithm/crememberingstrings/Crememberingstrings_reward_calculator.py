import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from string import ascii_lowercase
import re

# === 源文件中的全局函数 ===

def solve(n, m, strings, costs):
    faa = [[0] * m for _ in range(n)]
    famask = [[0] * m for _ in range(n)]
    
    for i in range(n):
        for j in range(m):
            current_char = strings[i][j]
            total_cost = 0
            max_cost = 0
            mask = 0
            for k in range(n):
                if strings[k][j] == current_char:
                    total_cost += costs[k][j]
                    if costs[k][j] > max_cost:
                        max_cost = costs[k][j]
                    mask |= (1 << k)
            faa[i][j] = total_cost - max_cost
            famask[i][j] = mask
    
    dp = [float('inf')] * (1 << n)
    dp[0] = 0
    
    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        for j in range(n):
            if (mask >> j) & 1:
                continue
            for k in range(m):
                new_mask1 = mask | (1 << j)
                cost1 = dp[mask] + costs[j][k]
                if cost1 < dp[new_mask1]:
                    dp[new_mask1] = cost1
                
                new_mask2 = mask | famask[j][k]
                cost2 = dp[mask] + faa[j][k]
                if cost2 < dp[new_mask2]:
                    dp[new_mask2] = cost2
    
    return dp[(1 << n) - 1]


class CrememberingstringsRewardCalculator(BaseRewardCalculator):
    """Crememberingstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # More robust extraction with multiple patterns
        patterns = [
            r'\[answer\](.*?)\[\/answer\]',  # 标准格式
            r'answer:\s*(\d+)',              # 无标签格式
            r'\\boxed{(\d+)}'                # LaTeX格式
        ]
        for pattern in reversed(patterns):
            matches = re.findall(pattern, output, re.DOTALL)
            if matches:
                try:
                    return int(matches[-1].strip())
                except:
                    continue
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == identity['correct_output']
        except:
            return False
    
    # 其他额外方法

