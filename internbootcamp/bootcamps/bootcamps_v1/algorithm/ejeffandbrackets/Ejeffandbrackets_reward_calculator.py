import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EjeffandbracketsRewardCalculator(BaseRewardCalculator):
    """Ejeffandbrackets奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            m = identity['m']
            a = identity['a']
            b = identity['b']
            correct = cls.compute_min_ink(n, m, a, b)
            return solution == correct
        except:
            return False
    
    # 其他额外方法

