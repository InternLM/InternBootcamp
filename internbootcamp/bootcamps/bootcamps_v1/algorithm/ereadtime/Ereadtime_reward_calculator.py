import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class EreadtimeRewardCalculator(BaseRewardCalculator):
    """Ereadtime奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        try:
            return int(matches[-1].strip()) if matches else None
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        h = sorted(identity['h'])
        p = sorted(identity['p'])
        
        # Edge case: empty check
        if not p or not h:
            return solution == 0
        
        # Binary search with precise coverage check
        def is_feasible(d):
            ptr = 0
            for pos in h:
                if ptr >= len(p):
                    return True
                # Calculate coverage range
                left = pos - d
                right = pos + d
                
                # Skip until first uncovered track
                if p[ptr] > right:
                    continue
                
                # Check impossible case
                if p[ptr] < left:
                    return False
                
                # Find maximal reachable track
                max_reach = right
                while ptr < len(p) and p[ptr] <= max_reach:
                    ptr += 1
            
            return ptr >= len(p)
        
        # Find minimal time
        low, high = 0, max(abs(h[0]-p[-1]), abs(h[-1]-p[0]))
        best = high
        
        while low <= high:
            mid = (low + high) // 2
            if is_feasible(mid):
                best = mid
                high = mid - 1
            else:
                low = mid + 1
        
        return solution == best
    
    # 其他额外方法

