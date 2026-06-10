import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DehabthexorcistRewardCalculator(BaseRewardCalculator):
    """Dehabthexorcist奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        lines = [line.strip() for line in last_match.split('\n') if line.strip()]
        if not lines:
            return None
        if lines[0] == '-1':
            return -1 if len(lines) == 1 else None
        try:
            n = int(lines[0])
            if n == 0:
                return [] if len(lines) == 1 else None
            if len(lines) < 2:
                return None
            elements = list(map(int, lines[1].split()))
            if len(elements) != n or any(e <= 0 for e in elements):
                return None
            return elements
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        u = identity['u']
        v = identity['v']
        
        if solution == -1:
            return u > v or (u % 2) != (v % 2)
        
        if isinstance(solution, list):
            if not solution:
                return u == 0 and v == 0
            if any(not isinstance(e, int) or e <= 0 for e in solution):
                return False
        else:
            return False
        
        xor = 0
        total = 0
        for num in solution:
            xor ^= num
            total += num
        
        if xor != u or total != v:
            return False
        
        if u > v or (u % 2) != (v % 2):
            return False
        
        if u == v:
            correct_len = 0 if u == 0 else 1
        else:
            x = (v - u) // 2
            correct_len = 3 if (x & u) else 2
        
        return len(solution) == correct_len
    
    # 其他额外方法

