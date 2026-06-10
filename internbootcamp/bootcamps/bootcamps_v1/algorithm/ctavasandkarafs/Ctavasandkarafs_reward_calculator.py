import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_r(A, B, l, t, m):
    v = A + (l - 1) * B
    if v > t:
        return -1

    lo, hi = 0, 10**8
    while lo < hi:
        mid = (lo + hi + 1) // 2
        sum_condition = (v + v + (mid - 1) * B) * mid
        right = t * min(m, mid) * 2
        if sum_condition > right:
            hi = mid - 1
        else:
            lo = mid

    if lo == 0:
        return -1

    max_r1 = l + lo - 1
    max_r2 = (t - A) // B + 1 if B != 0 else t
    r = min(max_r1, max_r2)
    return r if r >= l else -1


class CtavasandkarafsRewardCalculator(BaseRewardCalculator):
    """Ctavasandkarafs奖励计算器"""
    
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
        return solution == identity['expected_r']
    
    # 其他额外方法

