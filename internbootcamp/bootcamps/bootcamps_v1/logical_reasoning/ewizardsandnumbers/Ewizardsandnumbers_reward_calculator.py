import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EwizardsandnumbersRewardCalculator(BaseRewardCalculator):
    """Ewizardsandnumbers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](First|Second)\[/answer\]', output, re.IGNORECASE)
        return matches[-1].strip().title() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a, b = identity['a'], identity['b']
        a, b = sorted((a, b))
        correct = cls.win(a, b)
        return solution == ('First' if correct else 'Second')
    
    # 其他额外方法

