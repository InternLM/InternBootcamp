import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CrationalleeRewardCalculator(BaseRewardCalculator):
    """Crationallee奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            return int(last_answer)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        w = identity['w']
        n = identity['n']
        k = identity['k']
        # Sort a in descending order
        a_sorted = sorted(a, reverse=True)
        w_sorted = sorted(w)
        p = a_sorted[:k]
        x = k - 1
        ans = 0
        for i in range(k):
            wi = w_sorted[i]
            if wi == 1:
                ans += 2 * p[i]
            else:
                ans += p[i]
                x += wi - 1
                ans += a_sorted[x]
        return solution == ans
    
    # 其他额外方法

