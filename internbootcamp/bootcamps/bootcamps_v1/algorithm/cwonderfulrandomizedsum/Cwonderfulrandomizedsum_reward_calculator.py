import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CwonderfulrandomizedsumRewardCalculator(BaseRewardCalculator):
    """Cwonderfulrandomizedsum奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        arr = identity["array"]
        s1 = sum(arr)
        s2 = mx = 0
        for num in arr:
            s2 = max(s2 + num, 0)
            mx = max(mx, s2)
        return solution == 2 * mx - s1
    
    # 其他额外方法

