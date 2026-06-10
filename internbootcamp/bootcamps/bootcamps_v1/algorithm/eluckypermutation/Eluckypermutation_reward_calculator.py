import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque




class EluckypermutationRewardCalculator(BaseRewardCalculator):
    """Eluckypermutation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = cls._calculate_expected(identity['n'], identity['k'])
            return solution == expected
        except:
            return False
    
    # 其他额外方法

