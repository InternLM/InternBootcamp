import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_expected_probabilities(n, k, p_list):
    non_zero = [(idx, p) for idx, p in enumerate(p_list) if p > 1e-9]
    cnt = len(non_zero)
    real_k = min(k, cnt)
    
    if real_k >= cnt:
        expected = [0.0] * n
        for idx, p in non_zero:
            expected[idx] = 1.0
        return expected
    
    s = 1 << cnt
    sum_state = [0.0] * s
    for state in range(s):
        total = 0.0
        for j in range(cnt):
            if state & (1 << j):
                total += non_zero[j][1]
        sum_state[state] = total
    
    f = [0.0] * s
    f[0] = 1.0
    
    for state in range(1, s):
        for j in range(cnt):
            if state & (1 << j):
                prev = state ^ (1 << j)
                denominator = 1.0 - sum_state[prev]
                if denominator < 1e-9:
                    continue
                f[state] += f[prev] * non_zero[j][1] / denominator
    
    expected = [0.0] * n
    for state in range(s):
        pc = bin(state).count('1')
        if pc == real_k:
            for j in range(cnt):
                if state & (1 << j):
                    idx = non_zero[j][0]
                    expected[idx] += f[state]
    
    return expected


class ClruInstructionGenerator(BaseInstructionGenerator):
    """Clru Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, **kwargs):
        """
        初始化Clru指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        k = random.randint(1, n)
        
        # 生成和为100的整数分割（确保两位小数）
        total = 100
        parts = []
        for _ in range(n-1):
            part = random.randint(0, total)
            parts.append(part)
            total -= part
        parts.append(total)
        random.shuffle(parts)
        p = [x / 100.0 for x in parts]
        
        expected = compute_expected_probabilities(n, k, p)
        return {
            'n': n,
            'k': k,
            'p': p,
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        p = question_case['p']
        p_str = ' '.join(f"{pi:.2f}" for pi in p)
        prompt = (
            "You are tasked with calculating the probability of each video being present in an LRU (Least Recently Used) cache after 10^100 queries. The cache can hold up to k videos. Each query independently selects a video according to the given probabilities. Determine the steady-state probability for each video.\n\n"
            "Input format:\n"
            "- The first line contains two integers n and k (1 ≤ k ≤ n ≤ 20).\n"
            "- The second line contains n real numbers p1 p2 ... pn (sums to 1, each with up to two decimals).\n\n"
            "Output format:\n"
            "- Space-separated real numbers, each up to 15 decimal places, ensuring absolute/relative error ≤ 1e-6.\n\n"
            "Example Input:\n"
            "3 2\n"
            "0.30 0.20 0.50\n\n"
            "Example Output:\n"
            "0.675 0.485714285714286 0.839285714285714\n\n"
            "Your task:\n"
            f"{n} {k}\n"
            f"{p_str}\n\n"
            "Put your final answer within [answer] and [/answer], e.g., [answer]0.1 0.2 0.7[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def is_close(a, b, rel_tol=1e-6, abs_tol=1e-6):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
