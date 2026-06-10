import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from math import gcd




class AvasyaandtriangleInstructionGenerator(BaseInstructionGenerator):
    """Avasyaandtriangle Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**3, min_m=1, max_m=10**3, min_k=2, max_k=10**6, ensure_solvable=None):
        """
        初始化Avasyaandtriangle指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            min_k: 参数描述
            max_k: 参数描述
            ensure_solvable: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
        self.min_k = min_k
        self.max_k = max_k
        self.ensure_solvable = ensure_solvable
    
    def case_generator(self):
        max_attempts = 1000
        for _ in range(max_attempts):
            # 生成参数时根据 ensure_solvable 调整策略
            if self.ensure_solvable:
                n = random.randint(self.min_n, self.max_n)
                m = random.randint(self.min_m, self.max_m)
                a = random.randint(1, n)
                b = random.randint(1, m)
                numerator = 2 * n * m
                denominator = a * b
                if denominator == 0:
                    continue
                if numerator % denominator != 0:
                    continue
                k = numerator // denominator
                if k < self.min_k or k > self.max_k or k < 2:
                    continue
                points = [(0, 0), (a, 0), (0, b)]
                valid = all(0 <= x <= n and 0 <= y <= m for x, y in points)
                if valid:
                    return {
                        'n': n,
                        'm': m,
                        'k': k,
                        'solvable': True,
                        'points': points
                    }
            else:
                n = random.randint(self.min_n, self.max_n)
                m = random.randint(self.min_m, self.max_m)
                k = random.randint(self.min_k, self.max_k)
                solvable = (2 * n * m) % k == 0
                if self.ensure_solvable is not None and solvable != self.ensure_solvable:
                    continue

                if not solvable:
                    return {
                        'n': n,
                        'm': m,
                        'k': k,
                        'solvable': False,
                        'points': None
                    }

                was_even = False
                current_k = k
                if current_k % 2 == 0:
                    current_k //= 2
                    was_even = True

                g = gcd(current_k, n)
                k_j = current_k // g
                a = n // g
                b = m // k_j

                if not was_even:
                    if 2 * a <= n:
                        a *= 2
                    else:
                        b *= 2
                        if b > m:
                            continue

                points = [(0, 0), (a, 0), (0, b)]
                valid = all(0 <= x <= n and 0 <= y <= m for x, y in points)
                if valid:
                    return {
                        'n': n,
                        'm': m,
                        'k': k,
                        'solvable': True,
                        'points': points
                    }

        # Fallback for ensure_solvable=True
        if self.ensure_solvable:
            n, m = self.min_n, self.min_m
            a, b = n, m
            k = (2 * n * m) // (a * b)
            while k < 2 or (2 * n * m) % (a * b) != 0 or k < self.min_k or k > self.max_k:
                a = random.randint(1, n)
                b = random.randint(1, m)
                k = (2 * n * m) // (a * b)
            points = [(0, 0), (a, 0), (0, b)]
            return {
                'n': n,
                'm': m,
                'k': k,
                'solvable': True,
                'points': points
            }

        # Fallback for other cases
        n, m, k = self.max_n, self.max_m, self.max_k
        while (2 * n * m) % k == 0:
            k = random.randint(self.min_k, self.max_k)
        return {
            'n': n,
            'm': m,
            'k': k,
            'solvable': False,
            'points': None
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        target_expr = f"{n}×{m}/{k} = {n*m}/{k}"
        prompt = f"""Vasya has three integers n={n}, m={m}, and k={k}. He wants to find three integer points (x1, y1), (x2, y2), (x3, y3) such that:
- All coordinates satisfy 0 ≤ xi ≤ {n} and 0 ≤ yi ≤ {m} for i = 1, 2, 3.
- The area of the triangle formed by these points is exactly (n×m)/k = {target_expr}.

Determine if such points exist. If yes, output "YES" followed by the coordinates. Otherwise, output "NO".

Format your answer as:
[answer]
YES
x1 y1
x2 y2
x3 y3
[/answer]
or
[answer]
NO
[/answer]

Place your final answer within [answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

