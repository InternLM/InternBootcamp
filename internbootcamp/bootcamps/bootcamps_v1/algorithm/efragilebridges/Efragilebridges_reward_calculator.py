import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n_platforms, a):
    """动态规划解法，包含完整边界校验"""
    if n_platforms < 2:
        return 0
    if len(a) != n_platforms - 1:
        raise ValueError("Bridge count mismatch")
    
    n = n_platforms - 1
    x = a.copy()
    
    # 右侧DP初始化
    r = [[0, 0] for _ in range(n_platforms)]
    for i in range(n-1, -1, -1):
        # 计算r[i][1]
        if x[i] == 1:
            r[i][1] = 0
        else:
            next_i = i + 1
            r_next_1 = r[next_i][1] if next_i < n_platforms else 0
            sum_val = r_next_1 + x[i]
            r[i][1] = sum_val & (~1)
        
        # 计算r[i][0]
        next_i = i + 1
        r_next_0 = r[next_i][0] if next_i < n_platforms else 0
        if x[i] % 2 == 1:
            r[i][0] = max(r[i][1], x[i] + r_next_0)
        else:
            r[i][0] = max(r[i][1], (x[i]-1) + r_next_0)
    
    # 左侧DP初始化
    l = [[0, 0] for _ in range(n_platforms)]
    for i in range(1, n_platforms):
        bridge_idx = i-1
        if bridge_idx < 0:
            continue
            
        x_val = x[bridge_idx]
        # 计算l[i][1]
        if x_val == 1:
            l[i][1] = 0
        else:
            prev_i = i-1
            l_prev_1 = l[prev_i][1] if prev_i >= 0 else 0
            sum_val = l_prev_1 + x_val
            l[i][1] = sum_val & (~1)
        
        # 计算l[i][0]
        prev_i = i-1
        l_prev_0 = l[prev_i][0] if prev_i >= 0 else 0
        if x_val % 2 == 1:
            l[i][0] = max(l[i][1], x_val + l_prev_0)
        else:
            l[i][0] = max(l[i][1], (x_val-1) + l_prev_0)
    
    # 计算最大值
    max_score = 0
    for i in range(n_platforms):
        current = r[i][0] + l[i][0]
        max_score = max(max_score, current)
    return max_score


class EfragilebridgesRewardCalculator(BaseRewardCalculator):
    """Efragilebridges奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip().split()[-1])
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected']
    
    # 其他额外方法

