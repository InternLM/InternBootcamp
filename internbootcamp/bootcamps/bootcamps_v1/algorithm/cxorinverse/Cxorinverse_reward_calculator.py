import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_min_inversions(n, a):
    v = 30
    t = x = 0
    while v >= 0:  # 修正循环条件
        u = d = 0
        r = {}
        w = 1 << v
        for i in a:
            p = i >> (v + 1)
            b = i & w
            if b:
                key = 2*p + 1
                r[key] = r.get(key, 0) + 1
                d += r.get(2*p, 0)  # 修正d计算逻辑
            else:
                key = 2*p
                r[key] = r.get(key, 0) + 1
                d += r.get(2*p + 1, 0)  # 修正d计算逻辑
        for p in r:
            if p % 2:
                rp = r[p]
                cp = r.get(p-1, 0)
                u += (cp*(cp-1))//2 - (rp*(rp-1))//2 - ((cp-rp)*(cp-rp-1))//2
        if d > (u - d):
            x += w
            d = u - d
        t += d
        v -= 1
    return t, x


class CxorinverseRewardCalculator(BaseRewardCalculator):
    """Cxorinverse奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            last = matches[-1].strip().split()
            return (int(last[0]), int(last[1]))
        except (ValueError, IndexError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or len(solution) != 2:
            return False
        return (solution[0] == identity['expected_inversions'] and 
                solution[1] == identity['optimal_x'])
    
    # 其他额外方法

