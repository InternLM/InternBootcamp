import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CnekodoesmathsInstructionGenerator(BaseInstructionGenerator):
    """Cnekodoesmaths Bootcamp指令生成器"""
    
    def __init__(self, min_val=1, max_val=10**9):
        """
        初始化Cnekodoesmaths指令生成器
        
        Args:
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_val < 1:
            raise ValueError("min_val must be ≥1")
        if max_val < min_val:
            raise ValueError("max_val must be ≥ min_val")
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        if random.random() < 0.2:
            case_type = random.choice([
                ('equal', 1, 1),
                ('small_diff', 5, 10),
                ('prime_diff', 2, 5),
                ('large_diff', 10**9-100, 10**9)
            ])
            a, b = {
                'equal': (lambda: (x:=random.randint(1,10**9), x)),
                'small_diff': lambda: (random.randint(1,100), random.randint(1,100)+5),
                'prime_diff': lambda: (random.choice([2,3,5,7,11]), random.choice([2,3,5,7,11])+2),
                'large_diff': lambda: (10**9 - random.randint(1,1000), 10**9)
            }[case_type[0]]()
        else:
            a = random.randint(self.min_val, self.max_val)
            b = random.randint(self.min_val, self.max_val)
        
        return {
            'a': a,
            'b': b,
            'correct_k': self.solve(a, b)
        }
    
    @staticmethod
    def prompt_func(question_case):
        a = question_case['a']
        b = question_case['b']
        return f"""Neko遇到了一个数论问题：给定两个正整数a和b，找到最小非负整数k，使得a+k和b+k的最小公倍数最小。

**问题参数**
- a = {a}
- b = {b}

**求解要求**
1. 如果存在多个k能得到相同的最小LCM，返回最小的k值
2. 答案必须是非负整数
3. 请将最终答案放在[answer]和[/answer]标签之间

**示例格式**
如果正确答案是0，应写：[answer]0[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def gcd(a, b):
        while b:
            a, b = b, a % b
        return a

    @staticmethod
    def lcm(a, b):
        return a * b // Cnekodoesmathsbootcamp.gcd(a, b)

    @staticmethod
    def solve(a, b):
        if a == b:
            return 0
        if a > b:
            a, b = b, a
        delta = b - a
        best_k = 0
        best_lcm = Cnekodoesmathsbootcamp.lcm(a, b)

        factors = set()
        for fac in range(1, int(delta**0.5) + 1):
            if delta % fac == 0:
                factors.update({fac, delta//fac})

        for current_fac in sorted(factors, reverse=True):
            k = (current_fac - a % current_fac) % current_fac
            new_a = a + k
            new_b = b + k
            current_lcm = Cnekodoesmathsbootcamp.lcm(new_a, new_b)

            if (current_lcm < best_lcm) or (current_lcm == best_lcm and k < best_k):
                best_lcm = current_lcm
                best_k = k

        return best_k
