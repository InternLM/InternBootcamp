import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CtramRewardCalculator(BaseRewardCalculator):
    """Ctram奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*([0-9.]+)\s*\[/answer\]', output)
        if not matches:
            return None
        try:
            return float(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s = identity['s']
        x1 = identity['x1']
        x2 = identity['x2']
        t1 = identity['t1']
        t2 = identity['t2']
        p = identity['p']
        d = identity['d']
        
        # 计算正确答案
        walk_time = abs(x2 - x1) * t2
        if t1 >= t2:
            correct_time = walk_time
        else:
            # 计算电车首次到达x1的时间和方向
            if d == 1:
                if p <= x1:
                    t_wait = (x1 - p) * t1
                    dir_after = 1 if x1 < s else -1
                else:
                    t_wait = (s - p + s - x1) * t1
                    dir_after = -1
            else:  # d == -1
                if p >= x1:
                    t_wait = (p - x1) * t1
                    dir_after = -1 if x1 > 0 else 1
                else:
                    t_wait = (p + x1) * t1
                    dir_after = 1
            
            # 计算从x1到x2的行驶时间
            if dir_after == 1:
                if x2 >= x1:
                    t_ride = (x2 - x1) * t1
                else:
                    t_ride = (s - x1 + s - x2) * t1
            else:  # dir_after == -1
                if x2 <= x1:
                    t_ride = (x1 - x2) * t1
                else:
                    t_ride = (x1 + x2) * t1
            
            tram_time = t_wait + t_ride
            correct_time = min(tram_time, walk_time)
        
        # 验证答案
        try:
            return abs(solution - correct_time) < 1e-6
        except:
            return False
    
    # 其他额外方法

