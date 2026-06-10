import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class Cehabanda2operationtaskRewardCalculator(BaseRewardCalculator):
    """Cehabanda2operationtask奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            a = identity['a'].copy()
            n = identity['n']
            lines = solution.strip().split('\n')
            if not lines:
                return False
            
            m = int(lines[0])
            if m != len(lines)-1 or m < 0 or m > n+1:
                return False
            
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) != 3:
                    return False
                
                try:
                    op = int(parts[0])
                    i = int(parts[1])
                    x = int(parts[2])
                except ValueError:
                    return False
                
                if i < 1 or i > n:
                    return False
                
                if op == 1:
                    if not (0 <= x <= 1e6):
                        return False
                    for j in range(i):
                        a[j] += x
                elif op == 2:
                    if not (1 <= x <= 1e6):
                        return False
                    for j in range(i):
                        a[j] %= x
                else:
                    return False
            
            # Verify strict increasing
            for i in range(n-1):
                if a[i] >= a[i+1]:
                    return False
            return True
        
        except Exception as e:
            return False
    
    # 其他额外方法

