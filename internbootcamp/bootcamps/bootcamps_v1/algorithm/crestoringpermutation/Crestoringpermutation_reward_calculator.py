import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from bisect import bisect_right as bisect
import re




class CrestoringpermutationRewardCalculator(BaseRewardCalculator):
    """Crestoringpermutation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        if last_match == '-1':
            return -1
        try:
            return list(map(int, last_match.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        b = identity['b']
        expected = identity.get('expected')
        if solution == -1:
            return expected == -1
        if not isinstance(solution, list) or len(solution) != 2 * n:
            return False
        if set(solution) != set(range(1, 2 * n + 1)):
            return False
        for i in range(n):
            if min(solution[2*i], solution[2*i+1]) != b[i]:
                return False
        if expected != -1:
            return solution == expected
        return False
    
    # 其他额外方法

