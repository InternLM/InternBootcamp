import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import bisect
import random
import re




class BbornthiswayRewardCalculator(BaseRewardCalculator):
    """Bbornthisway奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n, m = identity['n'], identity['m']
        ta, tb, k = identity['ta'], identity['tb'], identity['k']
        a, b = identity['a'], identity['b']
        
        # Edge case: impossible to connect
        if k >= n or k >= m:
            return solution == -1
        
        max_time = -1
        valid = False
        for x in range(k+1):
            if x >= n: continue
            
            # Find earliest possible B flight
            arrive_b = a[x] + ta
            idx = bisect.bisect_left(b, arrive_b)
            
            # Check remaining deletions in B flights
            remaining_deletions = k - x
            if idx + remaining_deletions >= m:
                continue
            
            # Calculate arrival time
            candidate = b[idx + remaining_deletions] + tb
            max_time = max(max_time, candidate)
            valid = True
        
        expected = max_time if valid else -1
        return solution == expected
    
    # 其他额外方法

