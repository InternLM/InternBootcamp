import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CmarinaandvasyaRewardCalculator(BaseRewardCalculator):
    """Cmarinaandvasya奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        ans = matches[-1].strip().lower()
        if ans == "-1":
            return -1
        # Validate characters
        if all(c in 'abcdefghijklmnopqrstuvwxyz' for c in ans):
            return ans
        return None  # Invalid characters
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        t = identity['t']
        s1 = identity['s1']
        s2 = identity['s2']
        possible = identity['possible']
        
        if solution == -1:
            return not possible
        if not isinstance(solution, str) or len(solution) != n:
            return False
        # Check character validity
        if not all(c in 'abcdefghijklmnopqrstuvwxyz' for c in solution):
            return False
        # Calculate Hamming distances
        diff_s1 = sum(1 for a, b in zip(s1, solution) if a != b)
        diff_s2 = sum(1 for a, b in zip(s2, solution) if a != b)
        return diff_s1 == t and diff_s2 == t
    
    # 其他额外方法

