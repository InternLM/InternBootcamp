import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import isclose




class ElruRewardCalculator(BaseRewardCalculator):
    """Elru奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            submitted = list(map(float, solution.split()))
        except:
            return False
        n, k, p = identity['n'], identity['k'], identity['p']
        if len(submitted) != n:
            return False
        correct = cls.calculate_probabilities(n, k, p)
        for c, s in zip(correct, submitted):
            if not (abs(c - s) <= 1e-6 or (abs(c - s)/max(abs(c), 1e-6) <= 1e-6)):
                return False
        return True
    
    # 其他额外方法

