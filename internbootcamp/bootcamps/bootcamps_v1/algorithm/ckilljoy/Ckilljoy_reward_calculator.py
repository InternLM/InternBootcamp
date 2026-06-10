import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CkilljoyRewardCalculator(BaseRewardCalculator):
    """Ckilljoy奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_ans = int(solution)
        except ValueError:
            return False
        
        n, x, a = identity['n'], identity['x'], identity['a']
        
        if all(num == x for num in a):
            return user_ans == 0
        
        sum_diff = sum(x - num for num in a)
        has_infected = x in a
        
        if has_infected or sum_diff == 0:
            return user_ans == 1
        
        return user_ans == 2
    
    # 其他额外方法

