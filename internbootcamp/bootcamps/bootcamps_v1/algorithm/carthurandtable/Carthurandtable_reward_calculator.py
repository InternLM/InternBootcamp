import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re




class CarthurandtableRewardCalculator(BaseRewardCalculator):
    """Carthurandtable奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[ANSWER\](\d+)\[\/ANSWER\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            return solution == cls.calculate_min_energy(**identity)
        except:
            return False
    
    # 其他额外方法

