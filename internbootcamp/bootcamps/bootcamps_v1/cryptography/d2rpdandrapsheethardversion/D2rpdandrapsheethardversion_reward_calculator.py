import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class D2rpdandrapsheethardversionRewardCalculator(BaseRewardCalculator):
    """D2rpdandrapsheethardversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.strip().split(',')))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list) or len(solution) == 0:
            return False
        n = identity['n']
        k = identity['k']
        x0 = identity['x0']
        current_x = x0
        for i, y in enumerate(solution):
            if i >= n:
                return False
            if not (0 <= y <= 2 * 10**7):
                return False
            if y == current_x:
                return True
            current_x = cls.subtract_kits(y, current_x, k)
        return False
    
    # 其他额外方法

