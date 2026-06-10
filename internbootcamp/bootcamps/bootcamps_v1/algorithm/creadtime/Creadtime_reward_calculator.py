import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import inf

# === 源文件中的全局函数 ===

def calculate_min_time(n, m, h, p):
    h = sorted(h)
    p = sorted(p)
    ss = 0
    ll = 2 * 10**18  # A sufficiently large upper bound

    while ss < ll:
        avg = (ss + ll) // 2
        works = True
        hidx = 0
        pidx = 0

        while hidx < n and pidx < m:
            current_p = p[pidx]
            current_h = h[hidx]

            if current_h - current_p > avg:
                works = False
                break

            # Calculate the furthest right track covered
            getback_time = max(0, 2 * (current_h - current_p))
            also_to_right = max(0, avg - getback_time)
            left_time = max(0, current_h - current_p)
            remaining_time = max(0, (avg - left_time) // 2)
            furthest_right = current_h + max(also_to_right, remaining_time)

            # Move to the first p not covered by current head
            while pidx < m and p[pidx] <= furthest_right:
                pidx += 1

            hidx += 1

        if pidx < m:
            works = False

        if works:
            ll = avg
        else:
            ss = avg + 1

    return ss


class CreadtimeRewardCalculator(BaseRewardCalculator):
    """Creadtime奖励计算器"""
    
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
        if solution is None:
            return False
        n = identity["n"]
        m = identity["m"]
        h = identity["h"]
        p = identity["p"]
        correct_time = calculate_min_time(n, m, h, p)
        return solution == correct_time
    
    # 其他额外方法

