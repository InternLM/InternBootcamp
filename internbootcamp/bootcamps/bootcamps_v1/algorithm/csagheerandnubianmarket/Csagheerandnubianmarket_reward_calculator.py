import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, S, a):
    a_list = a.copy()
    def solve(k):
        if k == 0:
            return S  # 总成本0 <= S
        modified = [a_list[i] + (i + 1) * k for i in range(n)]
        modified_sorted = sorted(modified)
        sum_cost = sum(modified_sorted[:k])
        return S - sum_cost

    left = 0
    right = n + 1
    best_k = 0
    while left < right:
        mid = (left + right) // 2
        # 处理mid超出n的情况
        if mid > n:
            current = False
        else:
            res = solve(mid)
            current = res >= 0
        if current:
            best_k = mid
            left = mid + 1
        else:
            right = mid

    if best_k == 0:
        return (0, 0)
    else:
        modified = [a_list[i] + (i + 1) * best_k for i in range(n)]
        modified_sorted = sorted(modified)
        sum_cost = sum(modified_sorted[:best_k])
        return (best_k, sum_cost)


class CsagheerandnubianmarketRewardCalculator(BaseRewardCalculator):
    """Csagheerandnubianmarket奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 寻找最后一个[answer]标签内容
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            parts = list(map(int, last_match.split()))
            if len(parts) != 2:
                return None
            return (parts[0], parts[1])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
        user_k, user_T = solution
        return (
            user_k == identity['correct_k'] and 
            user_T == identity['correct_T']
        )
    
    # 其他额外方法

