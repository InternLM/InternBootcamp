import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CfleaRewardCalculator(BaseRewardCalculator):
    """Cflea奖励计算器"""
    
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
        n = identity['n']
        m = identity['m']
        s = identity['s']
        
        a = (n-1) % s + 1 if s != 0 else 1
        b = (n-1) // s + 1 if s != 0 else 1
        c = (m-1) % s + 1 if s != 0 else 1
        d = (m-1) // s + 1 if s != 0 else 1
        
        correct = a * b * c * d
        return solution == correct
    
    # 其他额外方法

