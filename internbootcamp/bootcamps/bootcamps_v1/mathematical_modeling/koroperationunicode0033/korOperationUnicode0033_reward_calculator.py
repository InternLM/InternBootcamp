import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import re
import random
from typing import Optional




class Koroperationunicode0033RewardCalculator(BaseRewardCalculator):
    """Koroperationunicode0033奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> Optional[str]:
        matches = re.findall(r'\[\[(.*?)\]\]', output)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: dict) -> bool:
        try:
            if identity['type'] == 'compute':
                actual = cls.parse_solution(solution)
                expected = cls.compute_expression(identity['expression'])
                return math.isclose(actual, expected, rel_tol=1e-9)
            else:
                X = int(solution)
                a = identity['equation']['a']
                b = identity['equation']['b']
                c = identity['equation']['c']
                return math.isclose(math.sqrt(math.sqrt(X) + a**2) * b, c, rel_tol=1e-9)
        except:
            return False
    
    # 其他额外方法

