import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CbasketballexerciseRewardCalculator(BaseRewardCalculator):
    """Cbasketballexercise奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output)
        if not matches:
            return None
        answer_str = matches[-1].strip()
        try:
            return int(answer_str)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        h1 = identity['h1']
        h2 = identity['h2']
        
        if n == 0:
            correct = 0
        else:
            dp1 = [0] * n
            dp2 = [0] * n
            dp1[0] = h1[0]
            dp2[0] = h2[0]
            for i in range(1, n):
                dp1[i] = max(dp2[i-1] + h1[i], dp1[i-1])
                dp2[i] = max(dp1[i-1] + h2[i], dp2[i-1])
            correct = max(dp1[-1], dp2[-1])
        
        return solution == correct
    
    # 其他额外方法

