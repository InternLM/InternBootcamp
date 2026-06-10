import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EnumbertransformationInstructionGenerator(BaseInstructionGenerator):
    """Enumbertransformation Bootcamp指令生成器"""
    
    def __init__(self, max_b=10**18, max_a_diff=10**18, **kwargs):
        """
        初始化Enumbertransformation指令生成器
        
        Args:
            max_b: 参数描述
            max_a_diff: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_b = max_b
        self.max_a_diff = max_a_diff
    
    def case_generator(self):
        k = random.randint(2, 15)
        # 确保生成的b不超过1e18且>=1
        max_b_valid = min(self.max_b, 10**18)
        b = random.randint(1, max_b_valid)
        # 确保a不超过1e18
        max_valid_diff = min(self.max_a_diff, 10**18 - b)
        a_diff = random.randint(0, max_valid_diff)
        a = b + a_diff
        return {'a': a, 'b': b, 'k': k}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        b = question_case['b']
        k = question_case['k']
        return f"""你需要将正整数{a}转换为{b}。每次操作可选：
1. 减1，耗时1秒。
2. 选择x（2≤x≤{k}），将a替换为a - (a mod x)，耗时1秒。
计算所需最少秒数，并将答案放在[answer]标签内。例如：[answer]5[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

