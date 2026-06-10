import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
import re




class CluckydaysRewardCalculator(BaseRewardCalculator):
    """Cluckydays奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output)
        if not matches:
            return None
        try:
            return int(matches[-1])
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a_la, a_ra, a_ta = identity['a_params']
        b_lb, b_rb, b_tb = identity['b_params']

        length_a = a_ra - a_la + 1
        length_b = b_rb - b_lb + 1
        gcd_val = math.gcd(a_ta, b_tb)
        phase_diff = b_lb - a_la

        ab_shift = phase_diff % gcd_val
        ba_shift = gcd_val - ab_shift

        overlap1 = min(length_a, length_b + ab_shift) - ab_shift
        overlap2 = min(length_a + ba_shift, length_b) - ba_shift

        correct = max(0, overlap1, overlap2)
        return solution == correct
    
    # 其他额外方法

