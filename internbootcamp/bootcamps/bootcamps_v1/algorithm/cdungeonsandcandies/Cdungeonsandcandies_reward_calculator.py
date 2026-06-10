import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CdungeonsandcandiesRewardCalculator(BaseRewardCalculator):
    """Cdungeonsandcandies奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        lines = solution.split('\n')
        if len(lines) != identity['k'] + 1:
            return False
        
        try:
            claimed = int(lines[0])
            pairs = [tuple(map(int, line.split())) for line in lines[1:]]
        except:
            return False
        
        if {x for x, _ in pairs} != set(range(1, identity['k']+1)):
            return False
        
        transmitted = set()
        total = 0
        for x, y in pairs:
            if y != 0 and y not in transmitted:
                return False
            if y == 0:
                total += identity['n'] * identity['m']
            else:
                diff = sum(c1 != c2 for r1, r2 in zip(identity['levels'][x-1], identity['levels'][y-1]) 
                          for c1, c2 in zip(r1, r2))
                total += diff * identity['w']
            transmitted.add(x)
        
        return total == claimed == identity['correct_total']
    
    # 其他额外方法

