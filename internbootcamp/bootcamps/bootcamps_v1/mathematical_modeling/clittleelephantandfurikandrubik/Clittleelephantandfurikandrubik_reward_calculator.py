import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_expected(n, a_str, b_str):
    a = [[[] for _ in range(26)] for __ in range(2)]
    for i, s in enumerate([a_str, b_str]):
        for j, c in enumerate(s):
            idx = ord(c) - ord('A')
            a[i][idx].append(j)
    
    total = 0
    for char_idx in range(26):
        p = a[0][char_idx]
        q = a[1][char_idx]
        if not p or not q:
            continue
        
        q_sum = sum(q)
        p_len = len(p)
        q_len = len(q)
        j = 0
        t = 0
        
        for x in p:
            # 维护双指针找到q中第一个不小于x的位置
            while j < q_len and q[j] < x:
                t += q[j]
                j += 1
            
            # 计算两项贡献（参考原算法逻辑）
            part1 = (t + j * x) * (n - x)
            part2 = (x + 1) * (n * (q_len - j) - (q_sum - t))
            total += part1 + part2
    
    # 计算分母：n*(n+1)*(2n+1)/6
    denominator = n * (n + 1) * (2 * n + 1) / 6
    if denominator == 0:
        return 0.0
    return total * 6.0 / (n * (n + 1) * (2 * n + 1))


class ClittleelephantandfurikandrubikRewardCalculator(BaseRewardCalculator):
    """Clittleelephantandfurikandrubik奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        # 处理科学计数法（如1e-9等）
        if 'e' in last_match:
            try:
                return "{0:.9f}".format(float(last_match))
            except:
                return None
        return last_match
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            solution_float = float(solution)
            expected = identity['expected']
            absolute_error = abs(solution_float - expected)
            
            # 处理极端情况（如期望为0时）
            if expected == 0:
                return absolute_error < 1e-6
            # 计算相对误差
            relative_error = absolute_error / abs(expected)
            return relative_error < 1e-6 or absolute_error < 1e-6
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

