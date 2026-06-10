import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_expected_time(n, r, levels):
    a = levels
    left = 0.0
    right = 1e18
    answer = 0.0
    dp = [[0.0] * 5001 for _ in range(n + 2)]

    for _ in range(100):
        middle = (left + right) / 2
        for i in range(n + 1):
            for j in range(5001):
                dp[i][j] = 0.0

        for i in range(n - 1, -1, -1):
            for j in range(r + 1, 5001):
                dp[i + 1][j] = middle
            Fi, Si, Pi = a[i]
            p = Pi / 100.0
            q = (100 - Pi) / 100.0
            for j in range(r, -1, -1):
                fast = j + Fi
                slow = j + Si
                val_fast = Fi + (dp[i + 1][fast] if fast <= r else middle)
                val_slow = Si + (dp[i + 1][slow] if slow <= r else middle)
                expected = p * val_fast + q * val_slow
                dp[i][j] = min(middle, expected)
        if dp[0][0] < middle - 1e-12:
            answer = middle
            right = middle
        else:
            left = middle
    return answer


class CgottagofastRewardCalculator(BaseRewardCalculator):
    """Cgottagofast奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return float(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['N']
            r = identity['R']
            levels = [(lev['F'], lev['S'], lev['P']) for lev in identity['levels']]
            correct = calculate_expected_time(n, r, levels)
            user_ans = float(solution)
            abs_err = abs(user_ans - correct)
            if abs_err <= 1e-9:
                return True
            rel_err = abs_err / max(1e-9, abs(user_ans), abs(correct))
            return rel_err <= 1e-9
        except:
            return False
    
    # 其他额外方法

