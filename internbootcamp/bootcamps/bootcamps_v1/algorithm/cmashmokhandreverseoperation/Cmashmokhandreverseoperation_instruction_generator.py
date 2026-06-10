import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answers(n, a, queries):
    aa = a.copy()
    m = len(queries)
    res = []
    
    if n == 0:
        return [0] * m  # Only one element, no possible inversions
    
    if n < 2:
        a1, a2 = aa[0], aa[1]
        original_inversion = 1 if a1 > a2 else 0
        reversed_inversion = 1 if a2 > a1 else 0
        current_inversion = original_inversion
        f = False  # Tracks whether the array is reversed
        for q in queries:
            if q != 0:
                f = not f
                current_inversion = reversed_inversion if f else original_inversion
            res.append(current_inversion)
        return res
    
    n2 = 2 ** n
    acc0 = []
    acc1 = []
    
    # Initialize for q=1 and q=2 levels
    a00 = a01 = a10 = a11 = 0
    for i in range(0, n2, 4):
        a_val = aa[i]
        b_val = aa[i+1] if i+1 < n2 else 0
        c_val = aa[i+2] if i+2 < n2 else 0
        d_val = aa[i+3] if i+3 < n2 else 0
        
        a00 += (b_val < a_val) + (d_val < c_val)
        a01 += (c_val < a_val) + (c_val < b_val) + (d_val < a_val) + (d_val < b_val)
        a10 += (b_val > a_val) + (d_val > c_val)
        a11 += (c_val > a_val) + (c_val > b_val) + (d_val > a_val) + (d_val > b_val)
    
    acc0 = [a00, a01]
    acc1 = [a10, a11]
    w = 4
    
    while w < n2:
        a00 = 0
        a10 = 0
        for i in range(0, n2, w * 2):
            le = sorted(aa[i:i + w])
            ri = sorted(aa[i + w:i + w * 2])
            
            # Compute a00 (inversions from left to right)
            i_le, j_ri, cnt = 0, 0, 0
            while i_le < len(le) and j_ri < len(ri):
                if le[i_le] > ri[j_ri]:
                    j_ri += 1
                else:
                    cnt += j_ri
                    i_le += 1
            cnt += j_ri * (len(le) - i_le)
            a00 += cnt
            
            # Compute a10 (inversions from right to left)
            i_ri, j_le, cnt = 0, 0, 0
            while i_ri < len(ri) and j_le < len(le):
                if ri[i_ri] > le[j_le]:
                    j_le += 1
                else:
                    cnt += j_le
                    i_ri += 1
            cnt += j_le * (len(ri) - i_ri)
            a10 += cnt
        
        acc0.append(a00)
        acc1.append(a10)
        w *= 2
    
    # Handling queries by swapping acc0 and acc1 as needed
    for q in queries:
        current_q = q
        # Flip all levels up to q
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
        res.append(sum(acc0))
        # Restore original state for next query
        for level in range(current_q):
            if level < len(acc0):
                acc0[level], acc1[level] = acc1[level], acc0[level]
                
    return res


class CmashmokhandreverseoperationInstructionGenerator(BaseInstructionGenerator):
    """Cmashmokhandreverseoperation Bootcamp指令生成器"""
    
    def __init__(self, max_n=3, m_min=1, m_max=5, **kwargs):
        """
        初始化Cmashmokhandreverseoperation指令生成器
        
        Args:
            max_n: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        n = random.randint(0, self.max_n)
        size_a = 2 ** n
        a = [random.randint(1, 10) for _ in range(size_a)] if size_a > 0 else []
        m = random.randint(self.m_min, self.m_max)
        valid_queries = [random.randint(0, n) for _ in range(m)]
        expected_outputs = compute_answers(n, a, valid_queries)
        return {
            'n': n,
            'a': a,
            'queries': valid_queries,
            'expected_outputs': expected_outputs
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        queries = question_case['queries']
        m = len(queries)
        problem_desc = f"""Cmashmokhandreverseoperation needs your help to solve an array transformation problem. Process a series of queries on an array and determine inversion counts after each transformation.

**Problem Rules:**
1. Start with an array of {2**n} elements: {a}
2. For each query q in {queries}:
   - Split the array into 2^(n - q) subarrays, each consisting of 2^q elements
   - Reverse each subarray
   - Reassemble the array while preserving subarray order
   - Compute the number of inversions in the new array and output it

**Task:**
Process all {m} queries in order and output the inversion count after each step. Provide your answers in [answer] tags with each result on a new line.

Example format:
[answer]
0
6
6
0
[/answer]

**Your Problem:**
Initial array (n={n}): {a}
Queries (m={m}): {queries}

Place your answers between [answer] and [/answer] tags, with each answer on a separate line:"""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

