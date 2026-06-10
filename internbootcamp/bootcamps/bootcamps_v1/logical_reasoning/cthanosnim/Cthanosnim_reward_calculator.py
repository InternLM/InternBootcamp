import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CthanosnimRewardCalculator(BaseRewardCalculator):
    """Cthanosnim奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(Alice|Bob)\s*\[/answer\]', output, re.I)
        return matches[-1].capitalize() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        sorted_piles = sorted(identity['piles'])
        n = identity['n']
        mid_index = n // 2
        return solution == ("Bob" if sorted_piles[0] == sorted_piles[mid_index] else "Alice")
    
    # 其他额外方法

