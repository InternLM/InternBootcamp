import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
import re




class CleavingthebarRewardCalculator(BaseRewardCalculator):
    """Cleavingthebar奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*([1\s-]+)\s*\[/answer\]', output)
        if not matches:
            return None
        try:
            return list(map(int, matches[-1].strip().split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if len(solution) != identity['n']:
            return False
        x_total, y_total = 0, 0
        for sign, (dx, dy) in zip(solution, identity['vectors']):
            x_total += sign * dx
            y_total += sign * dy
        return math.hypot(x_total, y_total) <= 1.5e6
    
    # 其他额外方法

