import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class BandsequencesRewardCalculator(BaseRewardCalculator):
    """Bandsequences奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output)
        if matches:
            try:
                return int(matches[-1])
            except ValueError:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity['a']
        n = identity['n']
        if n < 2:
            return False
        x = a[0]
        for num in a[1:]:
            x &= num
        c = a.count(x)
        if c < 2:
            correct = 0
        else:
            if n - 2 >= 0:
                fact = cls.fact[n - 2]
            else:
                fact = 1
            correct = (c * (c - 1) * fact) % MOD
        return solution == correct
    
    # 其他额外方法

