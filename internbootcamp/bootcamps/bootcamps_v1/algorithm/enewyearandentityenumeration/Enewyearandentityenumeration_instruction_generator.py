import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

mod = 10**9 + 7


class EnewyearandentityenumerationInstructionGenerator(BaseInstructionGenerator):
    """Enewyearandentityenumeration Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Enewyearandentityenumeration指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.m_min = params.get('m_min', 1)
        self.m_max = params.get('m_max', 5)
    
    def case_generator(self):
        m = random.randint(self.m_min, self.m_max)
        max_n = min(2**m, 50)
        n = random.randint(1, max_n)
        T = self._generate_binary_strings(m, n)
        correct_answer = self._compute_answer(m, T)
        return {
            'm': m,
            'n': n,
            'T': T,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        m = question_case['m']
        n = question_case['n']
        T = question_case['T']
        T_str = '\n'.join(T)
        return f"""You are given an integer m = {m} and a set T of {n} distinct binary strings of length {m}. Determine the number of good sets S modulo 10^9 + 7.

A good set S must satisfy:
1. For any x, y in S, x ^ y is in S.
2. For any x, y in S, x & y is in S.
3. All elements of T are in S.
4. Every element in S ≤ 2^{m} - 1.

Input Format:
{m} {n}
{T_str}

Output Format:
A single integer, the count modulo 10^9 + 7.

Example:
Input:
5 3
11010
00101
11000
Output:
4

Place your answer within [answer] and [/answer] tags, e.g., [answer]4[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_binary_strings(m, n):
        binaries = set()
        while len(binaries) < n:
            num = random.randint(0, (1 << m) - 1)
            binary = bin(num)[2:].zfill(m)
            binaries.add(binary)
        return list(binaries)

    @staticmethod
    def _Blist(m_val):
        A = [0] * m_val
        A[0] = 1
        R = [1, 1]
        for n in range(1, m_val):
            A[n] = A[0]
            for k in range(n, 0, -1):
                A[k-1] += A[k]
                A[k-1] %= mod
            R.append(A[0])
        return R

    @staticmethod
    def _compute_answer(m, T):
        n = len(T)
        t = [list(s) for s in T]
        ti = [int(''.join(row[k] for row in t), 2) for k in range(m)]
        left = set(range(m))
        gps = []
        while left:
            k = next(iter(left))
            current = ti[k]
            group = {j for j in left if ti[j] == current}
            left -= group
            gps.append(len(group))
        bell_numbers = Enewyearandentityenumerationbootcamp._Blist(m)
        res = 1
        for size in gps:
            res = res * bell_numbers[size] % mod
        return res
