import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpredictoutcomeofthegameRewardCalculator(BaseRewardCalculator):
    """Cpredictoutcomeofthegame奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](yes|no)\[/answer\]', output, re.IGNORECASE)
        return matches[-1].lower() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('_expected', None)
        if expected:
            return solution == expected
        else:
            n, k, d1, d2 = identity['n'], identity['k'], identity['d1'], identity['d2']
            return solution == ('yes' if cls.solve(n, k, d1, d2) else 'no')
    
    # 其他额外方法

