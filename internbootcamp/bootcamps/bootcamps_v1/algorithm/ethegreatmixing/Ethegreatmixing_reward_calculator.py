import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from itertools import combinations

# === 源文件中的全局函数 ===

def solve_case(n, c):
    if n in c:
        return 1
    q = {cc - n for cc in c}
    max_q = max(q)
    min_q = min(q)
    if max_q < 0 or min_q > 0:
        return -1
    max_positive = max_q
    min_negative_abs = -min_q
    maxs = [3000] * (max_positive + 1)
    mins = [3000] * (min_negative_abs + 1)
    for qq in q:
        if qq > 0 and qq <= max_positive:
            maxs[qq] = 1
        elif qq < 0:
            idx = -qq
            if idx <= min_negative_abs:
                mins[idx] = 1
    ans = float('inf')
    mni = len(mins) - 1
    mxi = len(maxs) - 1
    while mni > 0 and mxi > 0:
        if mni > mxi:
            mni, mxi = mxi, mni
            mins, maxs = maxs, mins
        for i in range(mni, 0, -1):
            if mxi - i >= 0:
                maxs[mxi - i] = min(maxs[mxi - i], maxs[mxi] + mins[i])
        mxi -= 1
        while mxi > 0 and maxs[mxi] > 2500:
            mxi -= 1
    final_min = min(maxs[0], mins[0])
    return final_min if final_min <= 2500 else -1


class EthegreatmixingRewardCalculator(BaseRewardCalculator):
    """Ethegreatmixing奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if matches:
            try:
                return int(matches[-1].strip())
            except:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == solve_case(identity['n'], identity['a'])
    
    # 其他额外方法

