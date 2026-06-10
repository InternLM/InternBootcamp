import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CgreedyarkadyRewardCalculator(BaseRewardCalculator):
    """Cgreedyarkady奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        k = identity['k']
        M = identity['M']
        D = identity['D']
        p = n // M
        ans = M * ((p - 1) // k + 1)
        for i in range(1, D + 1):
            split = (i - 1) * k + 1
            per = n // split
            if per > M:
                continue
            ans = max(ans, i * per)
        return solution == ans
    
    # 其他额外方法

