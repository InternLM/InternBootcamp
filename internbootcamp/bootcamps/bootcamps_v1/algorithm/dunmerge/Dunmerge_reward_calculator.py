import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DunmergeRewardCalculator(BaseRewardCalculator):
    """Dunmerge奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        solution = matches[-1].strip().upper()
        if solution not in ('YES', 'NO'):
            return None
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        p = identity['p']
        if not p:
            return False
        prev = p[0]
        sz = 0
        blocks = []
        for x in p:
            if x > prev:
                blocks.append(sz)
                sz = 0
                prev = x
            sz += 1
        blocks.append(sz)
        dp = [False] * (n + 1)
        dp[0] = True
        for b in blocks:
            for i in range(n, -1, -1):
                if dp[i] and (i + b) <= n:
                    if not dp[i + b]:
                        dp[i + b] = True
        expected_answer = 'YES' if dp[n] else 'NO'
        return solution.upper() == expected_answer
    
    # 其他额外方法

