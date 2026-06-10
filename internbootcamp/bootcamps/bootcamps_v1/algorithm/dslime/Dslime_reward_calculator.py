import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DslimeRewardCalculator(BaseRewardCalculator):
    """Dslime奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 保持原有验证逻辑不变
        a = identity['a']
        if len(a) == 1:
            return solution == a[0]
        
        total = sum(a)
        if any(x < 0 for x in a) ^ any(x >= 0 for x in a):
            min_val, max_val = min(a), max(a)
            return solution == ((total - 2*min_val) if any(x >=0 for x in a) else (2*max_val - total))
        return solution == sum(abs(x) for x in a)
    
    # 其他额外方法

