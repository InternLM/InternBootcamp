import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def geometric(k, lst):
    d = defaultdict(int)
    total = 0
    for num in lst:
        if k != 0 and num % k == 0:
            total += d.get((num // k, 2), 0)
            d[(num, 2)] += d.get((num // k, 1), 0)
        d[(num, 1)] += 1
    return total


class CgeometricprogressionRewardCalculator(BaseRewardCalculator):
    """Cgeometricprogression奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        k = identity['k']
        a = identity['a']
        return solution == geometric(k, a)
    
    # 其他额外方法

