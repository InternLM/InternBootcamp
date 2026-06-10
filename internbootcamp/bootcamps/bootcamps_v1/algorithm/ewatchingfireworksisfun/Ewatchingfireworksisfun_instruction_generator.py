import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math

# === 源文件中的全局函数 ===

def build_sparse_table(arr, n):
    log_table = [0] * (n + 1)
    for i in range(2, n + 1):
        log_table[i] = log_table[i // 2] + 1
    k_max = log_table[n] + 1
    st = [[0] * (n + 1) for _ in range(k_max)]
    for i in range(1, n + 1):
        st[0][i] = arr[i]
    for j in range(1, k_max):
        for i in range(1, n + 1 - (1 << j) + 1):
            st[j][i] = min(st[j-1][i], st[j-1][i + (1 << (j-1))])
    return st, log_table

def query_min(st, log_table, l, r):
    length = r - l + 1
    k = log_table[length]
    return min(st[k][l], st[k][r - (1 << k) + 1])

def calculate_answer(n, m, d, fireworks):
    sum_bi = sum(b for a, b, t in fireworks)
    a_list = [a for a, b, t in fireworks]
    t_list = [t for a, b, t in fireworks]
    
    prev_dp = [0] * (n + 2)
    a1 = a_list[0]
    for j in range(1, n + 1):
        prev_dp[j] = abs(a1 - j)
    
    for i in range(1, m):
        ai = a_list[i]
        ti = t_list[i]
        delta_t = ti - t_list[i-1]
        tt = d * delta_t
        tt = min(tt, n)
        
        st, log_table = build_sparse_table(prev_dp, n)
        curr_dp = [0] * (n + 2)
        
        for j in range(1, n + 1):
            left = max(1, j - tt)
            right = min(n, j + tt)
            if left > right:
                curr_dp[j] = float('inf')
            else:
                min_prev = query_min(st, log_table, left, right)
                curr_dp[j] = min_prev + abs(ai - j)
        
        prev_dp, curr_dp = curr_dp, prev_dp
    
    min_final = min(prev_dp[j] for j in range(1, n + 1))
    return sum_bi - min_final


class EwatchingfireworksisfunInstructionGenerator(BaseInstructionGenerator):
    """Ewatchingfireworksisfun Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ewatchingfireworksisfun指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.n = params.get('n', 50)
        self.m = params.get('m', 3)
        self.d = params.get('d', 1)
    
    def case_generator(self):
        n = random.randint(10, 50)
        m = random.randint(2, 5)
        d = random.randint(1, 5)
        fireworks = []
        t = 1
        for _ in range(m):
            ai = random.randint(1, n)
            bi = random.randint(1, 100)
            increment = random.randint(0, 5)
            t += increment
            fireworks.append((ai, bi, t))
        fireworks.sort(key=lambda x: x[2])  # Ensure ti is non-decreasing
        
        try:
            correct_answer = calculate_answer(n, m, d, fireworks)
        except:
            return self.case_generator()
        
        return {
            'n': n,
            'm': m,
            'd': d,
            'fireworks': fireworks,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        d = question_case['d']
        fireworks = question_case['fireworks']
        input_lines = [f"{n} {m} {d}"]
        for a, b, t in fireworks:
            input_lines.append(f"{a} {b} {t}")
        input_str = '\n'.join(input_lines)
        
        return f"""You are participating in a festival on a main street with {n} sections. Ewatchingfireworksisfun will be launched at specific times and sections. Your goal is to maximize the total happiness by positioning yourself optimally.

Rules:
1. You can move up to {d} units per time unit.
2. At each firework launch (time t_i), your happiness is calculated as (b_i - |a_i - x|), where x is your current section.
3. You start at any section at time 1.

Input format:
{input_str}

Calculate the maximum possible total happiness. Output the answer inside [answer] and [/answer] tags. For example: [answer]42[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

