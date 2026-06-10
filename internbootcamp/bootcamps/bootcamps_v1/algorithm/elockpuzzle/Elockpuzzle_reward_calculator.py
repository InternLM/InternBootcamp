import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string




class ElockpuzzleRewardCalculator(BaseRewardCalculator):
    """Elockpuzzle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        if not lines:
            return None
        if lines[0] == '-1':
            return -1
        
        try:
            k = int(lines[0])
            if len(lines) < 2:
                return None
            x_list = list(map(int, lines[1].split()))
            if len(x_list) != k:
                return None
            return x_list
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        s = identity['s']
        t = identity['t']
        
        # Check character composition
        if sorted(s) != sorted(t):
            return solution == -1
        
        # Check if solution is valid
        if solution == -1:
            return False
        
        if not isinstance(solution, list) or len(solution) > 6100:
            return False
        
        for x in solution:
            if not (0 <= x <= n):
                return False
        
        # Apply shifts to s
        current = s
        for x in solution:
            current = cls._apply_shift(current, x, n)
            if current is None:
                return False
        
        return current == t
    
    # 其他额外方法

