import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
import string




class CnamequestRewardCalculator(BaseRewardCalculator):
    """Cnamequest奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        s, t = identity['s'], identity['t']
        
        try:
            # 参考算法的完整实现
            i = -1
            for c in s:
                i = t.find(c, i + 1)
                if i == -1:
                    return int(solution) == 0
            
            l = i
            i = len(t)
            for c in reversed(s):
                i = t.rfind(c, 0, i)
                if i == -1:
                    return int(solution) == 0
            
            r = i
            correct = max(0, r - l) if l < r else 0
            return correct == int(solution)
        except:
            return False
    
    # 其他额外方法

