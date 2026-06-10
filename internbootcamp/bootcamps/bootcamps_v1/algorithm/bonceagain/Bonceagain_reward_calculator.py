import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import Counter




class BonceagainRewardCalculator(BaseRewardCalculator):
    """Bonceagain奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        try:
            return int(matches[-1]) if matches else None
        except (IndexError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        T = identity['T']
        a = identity['array']
        
        # Phase 1: Calculate first segment
        k = min(T, 2 * n)
        dp = [0] * 301
        for num in a * k:
            dp[num] = max(dp[:num+1]) + 1
        max_segment = max(dp)
        
        # Phase 2: Handle large T cases
        if T > 2 * n:
            counter = Counter(a)
            max_frequency = max(counter.values())
            return solution == max_segment + (T - 2 * n) * max_frequency
        
        return solution == max_segment
    
    # 其他额外方法

