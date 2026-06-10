import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from math import sqrt
from math import isclose
import random
import re




class EacolourfulprospectRewardCalculator(BaseRewardCalculator):
    """Eacolourfulprospect奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.search(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return int(match.group(1)) if match else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return solution == cls._compute_regions(identity)
        except:
            return False
    
    # 其他额外方法

