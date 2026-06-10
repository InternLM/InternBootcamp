import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 998244353


class E1chiorianddollpickingeasyversionInstructionGenerator(BaseInstructionGenerator):
    """E1chiorianddollpickingeasyversion Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, min_m=0, max_m=10, min_k=0, max_k=5):
        """
        初始化E1chiorianddollpickingeasyversion指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            min_k: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
        self.min_k = min_k
        # Ensure max_k doesn't exceed m//2 during case generation
        self.max_k = max_k
    
    def case_generator(self):
        m = random.randint(self.min_m, self.max_m)
        # Calculate maximum allowed k based on m//2 to ensure correctness
        max_k_allowed = m // 2 if m > 0 else 0
        max_k = min(self.max_k, max_k_allowed)
        k = random.randint(self.min_k, max_k) if max_k >= self.min_k else 0
        
        if m == 0:
            n = random.randint(self.min_n, self.max_n)
            a = [0] * n
            return {'n': n, 'm': m, 'a': a, 'correct_output': [pow(2, n, MOD)]}
        
        n = random.randint(max(k, self.min_n), self.max_n)
        basis = []
        for i in range(k):
            basis.append(1 << i)
        
        a = basis.copy()
        for _ in range(n - k):
            xor = 0
            selected = random.choices(basis, k=random.randint(0, k)) if k > 0 else []
            for num in selected:
                xor ^= num
            a.append(xor)
        random.shuffle(a)
        
        xor_sums = {0}
        for b in basis:
            new_xors = set()
            for x in xor_sums:
                new_xors.add(x ^ b)
            xor_sums.update(new_xors)
        
        bit_counts = {}
        for x in xor_sums:
            cnt = bin(x).count('1')
            bit_counts[cnt] = bit_counts.get(cnt, 0) + 1
        
        multiplier = pow(2, n - k, MOD)
        correct_output = [0] * (m + 1)
        for bits, count in bit_counts.items():
            if bits <= m:
                correct_output[bits] = (count * multiplier) % MOD
        
        return {'n': n, 'm': m, 'a': a, 'correct_output': correct_output}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        example_input = "4 4\n3 5 8 14"
        example_output = "2 2 6 6 0"
        prompt = f"""Chiori loves decorating her bedroom with dolls. As a doll collector, she has n dolls with certain values and wants to determine the number of ways to pick dolls such that the bitwise XOR sum of their values has a specific number of 1s in its binary form. 

Problem Statement:
You are given {question_case['n']} dolls with values listed below. Each value is a non-negative integer less than 2^{question_case['m']}. Calculate the number of ways to pick a subset (including picking none) such that the XOR sum of the selected dolls' values has exactly i 1s in its binary representation, for each i from 0 to {question_case['m']}. Output each count modulo 998244353.

Input:
- The first line contains two integers n and m: {question_case['n']} {question_case['m']}
- The second line contains the doll values: {' '.join(map(str, question_case['a']))}

Output:
Print {question_case['m']+1} integers p_0, p_1, ..., p_{question_case['m']} where each p_i is the count of subsets with exactly i 1s in the XOR sum's binary form, modulo 998244353.

Example Input:
{example_input}
Example Output:
{example_output}

Your Task:
Enclose your answer within [answer] and [/answer]. For example: [answer]0 1 2 3 4[/answer]
Ensure your answer includes all {question_case['m']+1} integers separated by spaces, even if some are zero.
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

