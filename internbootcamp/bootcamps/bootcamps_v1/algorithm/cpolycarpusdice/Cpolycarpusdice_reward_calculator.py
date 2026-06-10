import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CpolycarpusdiceRewardCalculator(BaseRewardCalculator):
    """Cpolycarpusdice奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return list(map(int, matches[-1].strip().split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity['n']
            A = identity['A']
            d = identity['d']
            sum_total = sum(d)
            correct = []
            for i in range(n):
                current = d[i]
                sum_others = sum_total - current
                part1 = max(0, A - sum_others - 1)
                part2 = max(0, current - (A - (n-1)))
                correct.append(part1 + part2)
            
            return solution == correct
        except:
            return False
    
    # 其他额外方法

