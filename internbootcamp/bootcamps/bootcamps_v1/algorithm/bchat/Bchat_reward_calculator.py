import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, k, links):
    x = [a - 1 for a in links]
    a = [0] * n
    for i in range(n):
        left = max(0, i - k)
        right = min(n - 1, i + k)
        visible = right - left + 1
        c = visible
        if x[i] != -1:
            if (i - x[i]) > 2 * k:
                c += a[x[i]]
            else:
                overlap_right = min(n - 1, x[i] + k)
                current_right = min(n - 1, i + k)
                additional = current_right - overlap_right
                c = a[x[i]] + additional
        a[i] = c
    return a


class BchatRewardCalculator(BaseRewardCalculator):
    """Bchat奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_output']
    
    # 其他额外方法

