import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CcelexupdateRewardCalculator(BaseRewardCalculator):
    """Ccelexupdate奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        m = identity['x2'] - identity['x1']
        n = identity['y2'] - identity['y1']
        return solution == m * n + 1
    
    # 其他额外方法

