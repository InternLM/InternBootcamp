import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CgukizhatesboxesRewardCalculator(BaseRewardCalculator):
    """Cgukizhatesboxes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            t = int(solution)
        except:
            return False
        
        return t == cls.compute_min_time(
            identity['n'],
            identity['m'],
            identity['a']
        )
    
    # 其他额外方法

