import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque
import math




class EgameontreeRewardCalculator(BaseRewardCalculator):
    """Egameontree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        pattern = r'\[answer\]\s*([\d.]+(?:e-?\d+)?)\s*\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            try:
                return float(matches[-1].replace(' ', ''))
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = identity['expected']
            actual = float(solution)
            return math.isclose(actual, expected, rel_tol=1e-9, abs_tol=1e-12)
        except (ValueError, TypeError):
            return False
    
    # 其他额外方法

