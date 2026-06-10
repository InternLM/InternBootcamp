import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class ErememberingstringsRewardCalculator(BaseRewardCalculator):
    """Erememberingstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = cls.calculate_min_cost(
                identity['n'], identity['m'],
                identity['strings'], identity['cost_matrix']
            )
            return solution == expected
        except:
            return False
    
    # 其他额外方法

