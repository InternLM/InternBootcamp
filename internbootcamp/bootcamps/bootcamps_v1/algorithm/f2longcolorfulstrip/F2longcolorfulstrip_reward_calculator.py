import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 998244353



# === 源文件中的全局函数 ===

def compute_answer(n_input, m_input, c_list):
    # Correctly map problem's n (number of colors) and m (strip length) to reference code's variables
    m_code = n_input  # Reference code's m represents problem's n (number of colors)
    n_code = m_input  # Reference code's n represents problem's m (strip length)

    C = [x - 1 for x in c_list]
    
    # Compress consecutive duplicates
    if not C:
        return 0
    C2 = [C[0]]
    for c in C[1:]:
        if C2[-1] != c:
            C2.append(c)
    new_n = len(C2)
    
    # Check if compressed length exceeds 2*m_code (problem's n)
    if new_n > 2 * m_code:
        return 0
    
    pos = [[] for _ in range(m_code)]
    for i in range(new_n):
        c = C2[i]
        if c >= m_code or c < 0:
            return 0
        pos[c].append(i)
    
    # Verify all colors are present
    for color in range(m_code):
        if not pos[color]:
            return 0
    
    DP = [[1] * (new_n + 1) for _ in range(new_n + 1)]
    
    for le in range(1, new_n + 1):
        for i in range(new_n - le + 1):
            j = i + le
            min_color = min(C2[i:j])
            min_indices = [p for p in range(i, j) if C2[p] == min_color]
            if not min_indices:
                DP[i][j] = 0
                continue
            
            first = min(min_indices)
            last = max(min_indices)
            
            # Calculate left part
            left = 0
            for k in range(i, first + 1):
                left = (left + DP[i][k] * DP[k][first]) % MOD
            
            # Calculate right part
            right = 0
            for k in range(last + 1, j + 1):
                right = (right + DP[last + 1][k] * DP[k][j]) % MOD
            
            # Calculate middle parts between occurrences of min_color
            middle = 1
            color_positions = pos[min_color]
            for idx in range(len(color_positions) - 1):
                prev = color_positions[idx]
                next_p = color_positions[idx + 1]
                if prev < i or next_p >= j:
                    continue
                middle = (middle * DP[prev + 1][next_p]) % MOD
            
            DP[i][j] = (left * right % MOD) * middle % MOD
    
    return DP[0][new_n]


class F2longcolorfulstripRewardCalculator(BaseRewardCalculator):
    """F2longcolorfulstrip奖励计算器"""
    
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
        n = identity['n']
        m = identity['m']
        c = identity['c']
        correct = compute_answer(n, m, c)
        return (solution % MOD) == (correct % MOD)
    
    # 其他额外方法

