import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CxorinverseInstructionGenerator(BaseInstructionGenerator):
    """Cxorinverse Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=1000, a_min=0, a_max=10**9):
        """
        初始化Cxorinverse指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.a_min = a_min
        self.a_max = a_max
    
    def case_generator(self):
        generation_strategy = random.choice([
            'zeros', 'uniform', 'random', 'high_bit_variation'
        ])
        
        n = random.randint(self.n_min, self.n_max)
        
        if generation_strategy == 'zeros':
            a = [0] * n
        elif generation_strategy == 'uniform':
            val = random.randint(self.a_min, self.a_max)
            a = [val] * n
        elif generation_strategy == 'high_bit_variation':
            base = random.randint(0, 1 << 20)
            a = [base ^ (random.randint(0, 1) << 30) for _ in range(n)]
        else:
            a = [random.randint(self.a_min, self.a_max) for _ in range(n)]
        
        t, x = solve_min_inversions(n, a)
        return {
            'n': n,
            'a': a,
            'expected_inversions': t,
            'optimal_x': x
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a_str = ' '.join(map(str, question_case['a']))
        return f"""You are given an array of {n} non-negative integers. Choose a non-negative integer x to form a new array b where each element b_i = a_i XOR x. Your goal is to minimize the number of inversions in b. If multiple x yield the same minimum, choose the smallest x.

Input:
{n}
{a_str}

Output format:
<inversion_count> <x>

Put your final answer within [answer] and [/answer] tags. Example: [answer]3 5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

