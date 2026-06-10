import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
from itertools import combinations




class CaupontrougeRewardCalculator(BaseRewardCalculator):
    """Caupontrouge奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return identity['candidates'][identity['k']-1] == solution
        except (IndexError, KeyError):
            return False
    
    # 其他额外方法

