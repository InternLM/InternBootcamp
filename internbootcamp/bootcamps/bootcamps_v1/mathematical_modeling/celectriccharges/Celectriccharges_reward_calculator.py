import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CelectricchargesRewardCalculator(BaseRewardCalculator):
    """Celectriccharges奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answers = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.DOTALL)
        if not answers:
            return None
        try:
            return int(answers[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        points = [tuple(p) for p in identity["points"]]
        return solution == cls._compute_min_diameter(points)
    
    # 其他额外方法

