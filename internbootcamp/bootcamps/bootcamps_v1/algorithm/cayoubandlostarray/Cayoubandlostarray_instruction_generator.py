import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, l, r):
    mod = 10**9 + 7

    def count_mod(low, high, m):
        remainder = low % 3
        if remainder <= m:
            first = low + (m - remainder)
        else:
            first = low + (3 - remainder + m)
        if first > high:
            return 0
        last = high - ((high - m) % 3)
        return ((last - first) // 3) + 1

    count0 = count_mod(l, r, 0)
    count1 = count_mod(l, r, 1)
    count2 = count_mod(l, r, 2)
    counts = [count0, count1, count2]

    # Dynamic programming approach
    dp_prev = counts.copy()
    for _ in range(n - 1):
        dp_next = [0] * 3
        for prev_mod in range(3):
            for curr_mod in range(3):
                new_mod = (prev_mod + curr_mod) % 3
                dp_next[new_mod] = (dp_next[new_mod] + dp_prev[prev_mod] * counts[curr_mod]) % mod
        dp_prev = dp_next

    return dp_prev[0] % mod


class CayoubandlostarrayInstructionGenerator(BaseInstructionGenerator):
    """Cayoubandlostarray Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=20, l_min=1, r_max=10**9):
        """
        初始化Cayoubandlostarray指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            l_min: 参数描述
            r_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.l_min = l_min
        self.r_max = r_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        l = random.randint(self.l_min, self.r_max)
        r = random.randint(l, self.r_max)
        correct_answer = compute_answer(n, l, r)
        return {
            'n': n,
            'l': l,
            'r': r,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        l = question_case['l']
        r = question_case['r']
        problem = f"""Given three integers n, l, and r, calculate the number of arrays of length n where each element is between l and r (inclusive) and the total sum is divisible by 3. Return the result modulo 10^9+7.

Input:
n = {n}, l = {l}, r = {r}

Put your final answer within [answer] tags like [answer]123[/answer]."""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

