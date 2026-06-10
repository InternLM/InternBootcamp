import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import math




class CtrailinglovesorloeufsRewardCalculator(BaseRewardCalculator):
    """Ctrailinglovesorloeufs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL | re.IGNORECASE)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
            
        n = identity['n']
        factors = identity['factors']
        if not factors:
            return solution == 0
        
        min_zeros = float('inf')
        for p, exp_in_base in factors:
            count = 0
            current = n
            while current > 0:
                current //= p
                count += current
            min_zeros = min(min_zeros, count // exp_in_base)
        
        return solution == min_zeros
    
    # 其他额外方法

