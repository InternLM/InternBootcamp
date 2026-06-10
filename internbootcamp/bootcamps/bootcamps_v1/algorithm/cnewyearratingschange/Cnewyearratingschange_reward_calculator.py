import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CnewyearratingschangeRewardCalculator(BaseRewardCalculator):
    """Cnewyearratingschange奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
        except ValueError:
            return None
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list):
            return False
        n = identity['n']
        a_list = identity['a']
        if len(solution) != n:
            return False
        
        sorted_a = sorted([(a, idx) for idx, a in enumerate(a_list)], key=lambda x: x[0])
        b = [0] * n
        current = 1
        for val, idx in sorted_a:
            current = max(val, current)
            b[idx] = current
            current += 1
        
        return solution == b
    
    # 其他额外方法

