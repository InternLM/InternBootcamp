import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_expected_probabilities(n, k, p_list):
    non_zero = [(idx, p) for idx, p in enumerate(p_list) if p > 1e-9]
    cnt = len(non_zero)
    real_k = min(k, cnt)
    
    if real_k >= cnt:
        expected = [0.0] * n
        for idx, p in non_zero:
            expected[idx] = 1.0
        return expected
    
    s = 1 << cnt
    sum_state = [0.0] * s
    for state in range(s):
        total = 0.0
        for j in range(cnt):
            if state & (1 << j):
                total += non_zero[j][1]
        sum_state[state] = total
    
    f = [0.0] * s
    f[0] = 1.0
    
    for state in range(1, s):
        for j in range(cnt):
            if state & (1 << j):
                prev = state ^ (1 << j)
                denominator = 1.0 - sum_state[prev]
                if denominator < 1e-9:
                    continue
                f[state] += f[prev] * non_zero[j][1] / denominator
    
    expected = [0.0] * n
    for state in range(s):
        pc = bin(state).count('1')
        if pc == real_k:
            for j in range(cnt):
                if state & (1 << j):
                    idx = non_zero[j][0]
                    expected[idx] += f[state]
    
    return expected


class ClruRewardCalculator(BaseRewardCalculator):
    """Clru奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        return last_match
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = identity['expected']
            parts = solution.split()
            if len(parts) != len(expected):
                return False
            for s_part, e_val in zip(parts, expected):
                s_val = float(s_part)
                if not cls.is_close(s_val, e_val):
                    return False
            return True
        except:
            return False
    
    # 其他额外方法

