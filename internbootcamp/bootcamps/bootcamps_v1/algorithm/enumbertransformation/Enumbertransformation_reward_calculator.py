import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import math

# === 源文件中的全局函数 ===

def lcm(a, b):
    return a * b // math.gcd(a, b)

def compute_mod(k):
    mod = 1
    for x in range(2, k+1):
        mod = lcm(mod, x)
    return mod

def dynamic_get(r1, r2, k):
    x_list = list(range(2, k+1))
    max_r = r2
    d = [float('inf')] * (max_r + 1)
    d[r1] = 0

    current_mods = [r1 % x for x in x_list]

    for i in range(r1 + 1, r2 + 1):
        new_mods = []
        min_steps = d[i-1] + 1
        for idx, x in enumerate(x_list):
            new_mod = current_mods[idx] + 1
            if new_mod >= x:
                new_mod = 0
            new_mods.append(new_mod)
            if new_mod != 0 and i - new_mod >= r1:
                candidate = d[i - new_mod] + 1
                if candidate < min_steps:
                    min_steps = candidate
        current_mods = new_mods
        d[i] = min_steps
    return d[r2]

def solve(a, b, k):
    if a == b:
        return 0
    mod = compute_mod(k)
    ra = a % mod
    rb = b % mod

    if a - b < mod and ra >= rb:
        return dynamic_get(rb, ra, k)
    else:
        part1 = dynamic_get(rb, mod - 1, k) + 1  # 上升到模的倍数
        part2 = dynamic_get(0, ra, k)
        cycle_num = (a - ra - (b - rb + mod)) // mod
        part3 = (dynamic_get(0, mod-1, k) + 1) * cycle_num
        return part1 + part2 + part3


class EnumbertransformationRewardCalculator(BaseRewardCalculator):
    """Enumbertransformation奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        a = identity.get('a', 0)
        b = identity.get('b', 0)
        k = identity.get('k', 0)
        # 严格验证输入参数合法性
        if not (1 <= b <= a <= 10**18) or not (2 <= k <=15):
            return False
        try:
            correct = solve(a, b, k)
            return solution == correct
        except:
            return False
    
    # 其他额外方法

