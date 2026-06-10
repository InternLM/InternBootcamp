import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import bisect
import random
import re




class CataleoftwolandsRewardCalculator(BaseRewardCalculator):
    """Cataleoftwolands奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = list(map(abs, identity['a']))
        a_sorted = sorted(a)
        n = identity['n']
        ans = 0
        for i in range(n):
            threshold = 2 * a_sorted[i]
            pos = bisect.bisect_right(a_sorted, threshold)
            ans += (pos - i - 1)
        return solution == ans
    
    # 其他额外方法

