import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CfractaldetectorRewardCalculator(BaseRewardCalculator):
    """Cfractaldetector奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            grid = [list(row) for row in identity['grid']]
            return cls.count_valid_fractals(grid) == solution
        except:
            return False
    
    # 其他额外方法

