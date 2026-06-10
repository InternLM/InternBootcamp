import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math

# === 源文件中的全局函数 ===

def build_sparse_table(arr, n):
    log_table = [0] * (n + 1)
    for i in range(2, n + 1):
        log_table[i] = log_table[i // 2] + 1
    k_max = log_table[n] + 1
    st = [[0] * (n + 1) for _ in range(k_max)]
    for i in range(1, n + 1):
        st[0][i] = arr[i]
    for j in range(1, k_max):
        for i in range(1, n + 1 - (1 << j) + 1):
            st[j][i] = min(st[j-1][i], st[j-1][i + (1 << (j-1))])
    return st, log_table

def query_min(st, log_table, l, r):
    length = r - l + 1
    k = log_table[length]
    return min(st[k][l], st[k][r - (1 << k) + 1])

def calculate_answer(n, m, d, fireworks):
    sum_bi = sum(b for a, b, t in fireworks)
    a_list = [a for a, b, t in fireworks]
    t_list = [t for a, b, t in fireworks]
    
    prev_dp = [0] * (n + 2)
    a1 = a_list[0]
    for j in range(1, n + 1):
        prev_dp[j] = abs(a1 - j)
    
    for i in range(1, m):
        ai = a_list[i]
        ti = t_list[i]
        delta_t = ti - t_list[i-1]
        tt = d * delta_t
        tt = min(tt, n)
        
        st, log_table = build_sparse_table(prev_dp, n)
        curr_dp = [0] * (n + 2)
        
        for j in range(1, n + 1):
            left = max(1, j - tt)
            right = min(n, j + tt)
            if left > right:
                curr_dp[j] = float('inf')
            else:
                min_prev = query_min(st, log_table, left, right)
                curr_dp[j] = min_prev + abs(ai - j)
        
        prev_dp, curr_dp = curr_dp, prev_dp
    
    min_final = min(prev_dp[j] for j in range(1, n + 1))
    return sum_bi - min_final


class EwatchingfireworksisfunRewardCalculator(BaseRewardCalculator):
    """Ewatchingfireworksisfun奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('correct_answer')
    
    # 其他额外方法

