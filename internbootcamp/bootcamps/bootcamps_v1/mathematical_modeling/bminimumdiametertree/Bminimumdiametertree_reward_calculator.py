import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque
import re




class BminimumdiametertreeRewardCalculator(BaseRewardCalculator):
    """Bminimumdiametertree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]([\d.]+)\[\/answer\]', output)
        return float(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution: return False
        expected = 2 * identity['s'] / identity['leaf_count']
        return abs(solution - expected) < 1e-6 * max(1, expected)
    
    # 其他额外方法

