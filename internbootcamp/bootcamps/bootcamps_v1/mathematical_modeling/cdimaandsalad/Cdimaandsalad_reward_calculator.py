import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
from collections import defaultdict
import random

# === 源文件中的全局函数 ===

def solve(n, k, a_list, b_list):
    b = [x * k for x in b_list]
    b2t = defaultdict(int)
    b2t[0] = 0
    for t, c in zip(a_list, b):
        bal = t - c
        updates = {}
        for ba in list(b2t.keys()):
            new_ba = ba + bal
            new_ta = b2t[ba] + t
            if new_ta > updates.get(new_ba, 0):
                updates[new_ba] = new_ta
        for key, val in updates.items():
            if val > b2t.get(key, 0):
                b2t[key] = val
    max_taste = b2t.get(0, 0)
    return max_taste if max_taste != 0 else -1


class CdimaandsaladRewardCalculator(BaseRewardCalculator):
    """Cdimaandsalad奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return int(solution) == identity['expected_output']
        except (ValueError, KeyError):
            return False
    
    # 其他额外方法

