import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CrectanglesRewardCalculator(BaseRewardCalculator):
    """Crectangles奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后一个出现的答案
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            # 允许多个空格分隔
            x, y = map(int, re.split(r'\s+', last_answer))
            return (x, y)
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        x, y = solution
        count = 0
        for rect in identity['rectangles']:
            x1, y1, x2, y2 = rect
            if x1 <= x <= x2 and y1 <= y <= y2:
                count += 1
        return count >= (identity['n'] - 1)
    
    # 其他额外方法

