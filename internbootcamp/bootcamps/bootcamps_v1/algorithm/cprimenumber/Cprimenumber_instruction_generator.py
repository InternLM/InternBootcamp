import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

mod = 10**9 + 7



# === 源文件中的全局函数 ===

def calculate_gcd_mod(n, x, a_list):
    sum_total = sum(a_list)
    b = [sum_total - ai for ai in a_list]
    vis = [False] * n
    ans = 1
    while True:
        current_min = None
        for i in range(n):
            if not vis[i] and (current_min is None or b[i] < current_min):
                current_min = b[i]
        if current_min is None or current_min == 0:
            break
        ans = ans * pow(x, current_min, mod) % mod
        count = 0
        new_sum = sum_total - current_min
        for i in range(n):
            if not vis[i]:
                b[i] -= current_min
                if b[i] == 0:
                    count += 1
        sum_total = new_sum
        if sum_total <= 0 or count % x != 0:
            break
        else:
            target = count // x
            p = 0
            for i in range(n):
                if not vis[i] and b[i] == 0:
                    if p < target:
                        b[i] = 1
                        p += 1
                    else:
                        vis[i] = True
    return ans % mod


class CprimenumberInstructionGenerator(BaseInstructionGenerator):
    """Cprimenumber Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, x_primes=None, a_max=10):
        """
        初始化Cprimenumber指令生成器
        
        Args:
            max_n: 参数描述
            x_primes: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_n = max_n
        self.x_primes = x_primes if x_primes is not None else [2, 3, 5, 7, 11]
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        x = random.choice(self.x_primes)
        a = sorted(random.randint(0, self.a_max) for _ in range(n))
        correct_answer = calculate_gcd_mod(n, x, a)
        return {
            'n': n,
            'x': x,
            'a': a,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        x = question_case['x']
        a = question_case['a']
        a_str = ' '.join(map(str, a))
        return f"""Simon has a prime number x and an array of non-negative integers. Your task is to compute the GCD of the fraction's numerator and denominator after summing 1/x^a_i for all elements. 

Input:
First line: {n} {x} (n and the prime x)
Second line: {a_str} (non-decreasing array)

Calculate the GCD modulo 1,000,000,007. Put your final answer within [answer] and [/answer] tags. Example: [answer]42[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

