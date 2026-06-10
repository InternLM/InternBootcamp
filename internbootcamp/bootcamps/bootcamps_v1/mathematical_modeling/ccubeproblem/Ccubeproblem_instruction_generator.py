import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random




class CcubeproblemInstructionGenerator(BaseInstructionGenerator):
    """Ccubeproblem Bootcamp指令生成器"""
    
    def __init__(self, max_abc=50):
        """
        初始化Ccubeproblem指令生成器
        
        Args:
            max_abc: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Initialize with parameters to control problem generation.
        :param max_abc: Maximum value for a, b, c (default 50)
        """
        self.max_abc = max_abc
    
    def case_generator(self):
        """
        Generates valid or invalid test cases:
        - Valid: n = 3*(a+b)(a+c)(b+c) with positive integers a, b, c
        - Invalid: n not divisible by 3
        """
        # Randomly choose valid or invalid cases
        if random.random() < 0.5:
            # Generate valid (a, b, c)
            a = random.randint(1, self.max_abc)
            b = random.randint(1, self.max_abc)
            c = random.randint(1, self.max_abc)
            n = 3 * (a + b) * (a + c) * (b + c)
        else:
            # Generate invalid n (not divisible by 3)
            n = random.randint(1, 10**14)
            while n % 3 == 0:
                n = random.randint(1, 10**14)
        
        answer = self.compute_answer(n)
        return {'n': n, 'answer': answer}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        prompt = f"""You are a programming assistant solving a mathematical puzzle. 

Problem:
Given an integer n, compute the number of ordered triples (a, b, c) of positive integers that satisfy:
3 × (a + b)(a + c)(b + c) = {n}

Input:
A single integer n (1 ≤ n ≤ 1e14).

Output:
The number of valid triples. If none exist, output 0.

Examples:
Input: 24 → Output: 1
Input: 5 → Output: 0

Answer within [answer]...[/answer] tags. For example: [answer]0[/answer].

Your task:
Given n = {n}, provide the correct answer."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n):
        if n % 3 != 0:
            return 0
        m = n // 3
        ans = 0
        i = 2
        while i * i * i <= m:
            if m % i != 0:
                i += 1
                continue
            r = m // i
            # Calculate j start value
            sqrt_val = math.isqrt(i * i + 4 * r)
            j_start_candidate = (-i + sqrt_val) // 2 - 10
            j_start = max(i, j_start_candidate, 1)
            max_j = math.isqrt(r)
            j = j_start
            while j <= max_j:
                if r % j == 0:
                    k = r // j
                    a_comb = i - j + k
                    b_comb = i + j - k
                    c_comb = -i + j + k
                    if (a_comb > 0 and b_comb > 0 and c_comb > 0 
                        and a_comb % 2 == 0):
                        a = a_comb // 2
                        b = b_comb // 2
                        c = c_comb // 2
                        if a > 0 and b > 0 and c > 0:
                            if a == b and b == c:
                                ans += 1
                            elif a == b or a == c or b == c:
                                ans += 3
                            else:
                                ans += 6
                j += 1
            i += 1
        return ans
