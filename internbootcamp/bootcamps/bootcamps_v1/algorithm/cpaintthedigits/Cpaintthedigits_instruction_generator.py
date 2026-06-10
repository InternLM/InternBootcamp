import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpaintthedigitsInstructionGenerator(BaseInstructionGenerator):
    """Cpaintthedigits Bootcamp指令生成器"""
    
    def __init__(self, solvable_probability=0.5, min_length=1, max_length=10):
        """
        初始化Cpaintthedigits指令生成器
        
        Args:
            solvable_probability: 参数描述
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.solvable_probability = solvable_probability
        self.min_length = max(1, min_length)
        self.max_length = max(max_length, self.min_length)
    
    def case_generator(self):
        if random.random() < self.solvable_probability:
            # Generate solvable case
            n = random.randint(self.min_length, self.max_length)
            sorted_digits = self.generate_non_decreasing(n)
            split_pos = random.randint(0, n)
            c1 = sorted_digits[:split_pos]
            c2 = sorted_digits[split_pos:]
            
            # Build original sequence with color assignment
            merged = []
            i = j = 0
            while i < len(c1) or j < len(c2):
                if random.choice([True, False]) and i < len(c1) or j >= len(c2):
                    merged.append(('1', c1[i]))
                    i += 1
                else:
                    merged.append(('2', c2[j]))
                    j += 1
            
            # Create final digits string
            digits = ''.join(str(d) for (_, d) in merged)
            return {'n': len(digits), 'digits': digits}
        else:
            # Generate unsolvable case (strictly decreasing with length >= 2)
            n = random.randint(max(2, self.min_length), self.max_length)
            digits = [str(9 - i % 10) for i in range(n)]
            return {'n': n, 'digits': ''.join(digits)}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        digits = question_case['digits']
        return f"""Given the digit sequence {digits}, color each digit with 1 or 2 such that:
1. All 1-colored digits in their original order
2. All 2-colored digits in their original order
3. Concatenation of 1's then 2's is non-decreasing

Provide your answer as a string of '1's and '2's with the same length, or '-' if impossible. Enclose your final answer within [answer] tags.

Example:
Input: 914
Answer: [answer]211[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_non_decreasing(self, length):
        if length == 0:
            return []
        sequence = [random.randint(0, 9)]
        for _ in range(length-1):
            sequence.append(random.randint(sequence[-1], 9))
        return sequence

    @staticmethod
    def solve(N, A):
        B = ['1'] * N
        last_1 = -1
        transition_point = None
        last_2 = -1

        for i in range(N):
            current = A[i]

            if last_1 == -1:
                last_1 = current
                continue

            if current >= last_1:
                last_1 = current
                continue

            if transition_point is None:
                # Find transition point
                transition_point = i
                min_2_val = current
                for m in range(current + 1, 10):
                    for j in range(i):
                        if A[j] == m and B[j] == '1':
                            transition_point = j
                            min_2_val = m
                            break
                    else:
                        continue
                    break
                else:
                    return '-'

                # Update colors for transition segment
                for j in range(transition_point):
                    if A[j] >= min_2_val:
                        B[j] = '2'
                last_2 = max(A[transition_point:i], default=-1)
                last_1 = current
            else:
                if current < last_1 or (current > last_2 and last_2 != -1):
                    return '-'
                if current >= last_2:
                    B[i] = '2'
                    last_2 = current
                else:
                    last_1 = current
        return ''.join(B)
