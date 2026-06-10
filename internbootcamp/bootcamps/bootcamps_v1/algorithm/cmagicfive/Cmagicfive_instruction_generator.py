import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CmagicfiveInstructionGenerator(BaseInstructionGenerator):
    """Cmagicfive Bootcamp指令生成器"""
    
    def __init__(self, a_min_length=1, a_max_length=5, k_min=1, k_max=1000, prob_05=0.4):
        """
        初始化Cmagicfive指令生成器
        
        Args:
            a_min_length: 参数描述
            a_max_length: 参数描述
            k_min: 参数描述
            k_max: 参数描述
            prob_05: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.a_min_length = max(1, a_min_length)
        self.a_max_length = max(a_min_length, a_max_length)
        self.k_min = max(1, k_min)
        self.k_max = max(k_min, k_max)
        self.prob_05 = prob_05
    
    def case_generator(self):
        if random.random() < self.prob_05:
            a = self._gen_has_05()
        else:
            a = self._gen_random()
        k = random.randint(self.k_min, self.k_max)
        return {'a': a, 'k': k}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        k = question_case['k']
        return f"""You are trying to solve a mathematical puzzle involving divisibility by 5. The puzzle's details are as follows:

Problem Description:
You are given a string 'a' consisting of digits and an integer 'k'. The string 's' is formed by concatenating 'a' exactly 'k' times. For example, if a is "12" and k is 3, then s is "121212".

Your task is to determine the number of distinct ways to delete some (but not all) digits from 's' such that the remaining digits form a number divisible by 5. The result should be computed modulo 1e9+7 (1000000007).

Rules:
1. A valid way of deletion must leave at least one digit remaining.
2. Two deletion methods are considered different if the sets of positions deleted are different, even if the resulting number is the same.
3. Leading zeros in the resulting number are allowed. For example, "005" is a valid number if divisible by 5.

Input Details:
- The string 'a' is "{a}" (length: {len(a)} characters).
- The integer 'k' is {k}.

Your task is to compute the number of valid deletion ways, taking into account the modulo requirement. Provide your final answer as an integer inside [answer] tags. For example, if your answer is 42, write [answer]42[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _gen_has_05(self):
        length = random.randint(self.a_min_length, self.a_max_length)
        chars = []
        for _ in range(length):
            if random.random() < 0.3:
                chars.append(random.choice(['0', '5']))
            else:
                chars.append(random.choice('12346789'))
        if not any(c in {'0','5'} for c in chars):
            chars[random.randint(0, len(chars)-1)] = random.choice(['0','5'])
        return ''.join(chars)

    def _gen_random(self):
        length = random.randint(self.a_min_length, self.a_max_length)
        return ''.join(random.choices('0123456789', k=length))

    @staticmethod
    def compute_ways(a, k):
        MOD = 10**9 + 7
        if not a:
            return 0

        l = len(a)
        two_l = pow(2, l, MOD)
        denominator = (two_l - 1) % MOD
        inv_denominator = pow(denominator, MOD-2, MOD) if denominator != 0 else 0

        power_sum = pow(two_l, k, MOD)

        base_sum = 0
        pwr = 1  # 对应2^0
        for char in a:
            if char in {'0', '5'}:
                base_sum = (base_sum + pwr) % MOD
            pwr = (pwr * 2) % MOD

        if inv_denominator == 0:
            total = 0
        else:
            numerator = (base_sum * (power_sum - 1 + MOD)) % MOD
            total = (numerator * inv_denominator) % MOD
        return total
