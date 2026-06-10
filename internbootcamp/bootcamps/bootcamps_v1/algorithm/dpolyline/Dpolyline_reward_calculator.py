import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DpolylineRewardCalculator(BaseRewardCalculator):
    """Dpolyline奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        points = identity['points']
        x = [p[0] for p in points]
        y = [p[1] for p in points]
        sx, sy = len(set(x)), len(set(y))
        
        # 核心验证逻辑
        if sx == 1 or sy == 1:
            return solution == 1
        elif sx == 2 and sy == 2:
            return solution == 2
        elif sx == 2:
            mid_y = sorted(y)[1]
            return solution == (3 if any(p[1] == mid_y for p in points) else 2)
        elif sy == 2:
            mid_x = sorted(x)[1]
            return solution == (3 if any(p[0] == mid_x for p in points) else 2)
        else:
            return solution == 3
    
    # 其他额外方法

