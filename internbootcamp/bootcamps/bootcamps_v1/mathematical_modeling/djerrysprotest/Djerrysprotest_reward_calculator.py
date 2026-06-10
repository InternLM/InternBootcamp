import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_probability(n, a_list):
    a = {}
    for i in range(n-1):
        for j in range(i+1, n):
            x = abs(a_list[i] - a_list[j])
            a[x] = a.get(x, 0) + 1

    d = list(a.keys())
    b = [0] * 10005

    for i in range(len(d)):
        for j in range(i, len(d)):
            key_i = d[i]
            key_j = d[j]
            sum_key = key_i + key_j
            contribution = a[key_i] * a[key_j]
            if key_i != key_j:
                contribution *= 2
            if sum_key < len(b):
                b[sum_key] += contribution

    for i in range(1, len(b)):
        b[i] += b[i-1]

    ans = 0
    for i in range(n-1):
        for j in range(i+1, n):
            s = abs(a_list[i] - a_list[j])
            if s - 1 >= 0 and s - 1 < len(b):
                ans += b[s - 1]

    den = (n * (n-1) // 2) ** 3
    return ans / den if den != 0 else 0.0

def is_close(a, b, rel_tol=1e-6, abs_tol=1e-6):
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


class DjerrysprotestRewardCalculator(BaseRewardCalculator):
    """Djerrysprotest奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_value = matches[-1].strip()
        try:
            return float(re.sub(r'[^\d.eE-]', '', last_value))
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_ans = float(solution)
        except:
            return False
        
        n = identity['n']
        a = identity['a']
        correct = calculate_probability(n, a)
        return is_close(user_ans, correct)
    
    # 其他额外方法

