import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CinnaandcandyboxesInstructionGenerator(BaseInstructionGenerator):
    """Cinnaandcandyboxes Bootcamp指令生成器"""
    
    def __init__(self, k_min=1, k_max=10, n_min=5, n_max=15, w_min=1, w_max=5, **kwargs):
        """
        初始化Cinnaandcandyboxes指令生成器
        
        Args:
            k_min: 参数描述
            k_max: 参数描述
            n_min: 参数描述
            n_max: 参数描述
            w_min: 参数描述
            w_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.k_min = max(k_min, 1)
        self.k_max = min(k_max, 10)  # Enforce k ≤ 10
        self.n_min = max(n_min, self.k_min)  # Ensure n ≥ k_min
        self.n_max = max(n_max, self.n_min)
        self.w_min = max(w_min, 1)
        self.w_max = max(w_max, self.w_min)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        k = random.randint(self.k_min, min(n, self.k_max))  # Force k ≤ min(n,10)
        
        # Generate valid candy configuration
        s = ''.join(random.choice('01') for _ in range(n))
        
        # Generate guaranteed valid queries
        w = random.randint(self.w_min, self.w_max)
        queries = [self.generate_valid_query(n, k) for _ in range(w)]
        
        return {
            'n': n,
            'k': k,
            'w': w,
            's': s,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Inna has {question_case['n']} boxes arranged in a row (1-indexed). Each box contains 1 (candy) or 0 (empty). Answer {question_case['w']} queries about intervals [l, r] where (r-l+1) is divisible by {question_case['k']}. For each query, ensure candies only appear at positions l+{question_case['k']-1}, l+{2*question_case['k']-1}, ..., r. Compute minimum add/remove operations.

Input:
{question_case['n']} {question_case['k']} {question_case['w']}
{question_case['s']}
""" + '\n'.join(f"{l} {r}" for l, r in question_case['queries']) + """

Format answers as:
[answer]
ans1
ans2
...
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_query(self, n, k):
        max_attempts = 100
        for _ in range(max_attempts):
            # Ensure li allows at least 1k-length interval
            li = random.randint(1, max(1, n - k + 1))
            max_possible_length = n - li + 1
            m_max = max_possible_length // k  # At least 1
            m = random.randint(1, m_max)
            ri = li + m*k - 1
            if ri <= n:
                return (li, ri)

        # Fallback: first valid interval
        return (1, k)

    @staticmethod
    def solve_case(n, k, w, s, queries):
        # Build prefix sum array with offset
        offset = k + 1
        prefix = [0] * (n + 2*offset)
        for i in range(n):
            prefix[i + offset] = prefix[i] + (1 if s[i] == '1' else 0)

        answers = []
        for l, r in queries:
            # Calculate required positions
            target_length = r - l + 1
            steps = target_length // k  # Number of required positions

            # Calculate required changes
            required_add = steps - sum(1 for i in range(steps) if s[l + i*k - 1] == '1')
            other_remove = sum(1 for pos in range(l-1, r) if (pos - (l-1)) % k != k-1 and s[pos] == '1')
            answers.append(required_add + other_remove)
        return answers
