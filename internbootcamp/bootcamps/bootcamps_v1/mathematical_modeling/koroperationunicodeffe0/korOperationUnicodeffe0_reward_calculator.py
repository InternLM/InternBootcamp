import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
from fractions import Fraction
import re




class Koroperationunicodeffe0RewardCalculator(BaseRewardCalculator):
    """Koroperationunicodeffe0奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            if identity['type'] == 'compute':
                if identity.get('is_expressible', True):
                    return Fraction(solution) == Fraction(identity['target'])
                else:
                    given = re.sub(r'\s+', '', solution)
                    expected = re.sub(r'\s+', '', identity['log_expr'])
                    return given == expected
            else:
                return int(solution) == identity['solution']
        except:
            return False
    
    # 其他额外方法

