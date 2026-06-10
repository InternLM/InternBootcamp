import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from io import StringIO
import sys




class DflipthecardsRewardCalculator(BaseRewardCalculator):
    """Dflipthecards奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强正则匹配，处理多空格情况
        matches = re.findall(r'\[answer\s*\]\s*(-?\d+)\s*\[/answer\s*\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_output']
    
    # 其他额外方法

