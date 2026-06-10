import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random




class CjzzhuandapplesRewardCalculator(BaseRewardCalculator):
    """Cjzzhuandapples奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        answer = matches[-1].strip().split('\n')
        try:
            m = int(answer[0])
            pairs = [tuple(map(int, line.split())) for line in answer[1:m+1]]
            if len(pairs) != m:
                return None
            return pairs
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return identity['m_correct'] == 0
        
        n = identity['n']
        expected_m = identity['m_correct']
        
        if len(solution) != expected_m:
            return False
        
        used = set()
        for a, b in solution:
            if a < 1 or b < 1 or a > n or b > n:
                return False
            if math.gcd(a, b) == 1:
                return False
            if a in used or b in used:
                return False
            used.update({a, b})
        
        return True
    
    # 其他额外方法

