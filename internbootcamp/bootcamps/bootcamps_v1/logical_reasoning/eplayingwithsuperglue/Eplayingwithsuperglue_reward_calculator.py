import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EplayingwithsuperglueRewardCalculator(BaseRewardCalculator):
    """Eplayingwithsuperglue奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # Match last occurrence with flexible tag closing
        matches = re.findall(r'\[answer\](.*?)(?=\s*\[/?answer\]|$)', output, re.IGNORECASE | re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().lower()
        if answer in ('first', 'second'):
            return answer.capitalize()
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        x1, y1 = identity['x1'], identity['y1']
        x2, y2 = identity['x2'], identity['y2']
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        
        # Ensure dx >= dy
        if dx < dy:
            dx, dy = dy, dx
        
        # Check winning conditions
        first_wins = (dx <= 3 and dy <= 3) or (dx, dy) in {(4,0), (4,1), (4,2)}
        return (solution == 'First') == first_wins
    
    # 其他额外方法

