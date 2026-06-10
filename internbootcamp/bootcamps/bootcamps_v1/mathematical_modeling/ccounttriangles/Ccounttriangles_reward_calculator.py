import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_answer(A, B, C, D):
    len_f = D - B + 2
    f = [0] * len_f

    for y in range(B, C + 1):
        start = C - y
        end = D - y + 1
        if start < len_f:
            f[start] += 1
        if end < len_f and end > 0:
            f[end] -= 1

    ans = f[0] * (B - A + 1)
    for d in range(1, B):
        if d >= len_f:
            break
        f[d] += f[d-1]
        current_min = min(B - A + 1, B - d)
        ans += f[d] * current_min

    return ans


class CcounttrianglesRewardCalculator(BaseRewardCalculator):
    """Ccounttriangles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

