import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpalindrometransformationRewardCalculator(BaseRewardCalculator):
    """Cpalindrometransformation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if identity['sum_updown'] == 0:
            return solution == 0
        
        try:
            user_ans = int(solution)
            l = identity['left']
            r = identity['right']
            p = identity['adjusted_p']
            
            # Calculate minimal movement cost
            movement = (r - l) + min(abs(p - l), abs(r - p))
            correct = identity['sum_updown'] + movement
            return user_ans == correct
        except:
            return False
    
    # 其他额外方法

