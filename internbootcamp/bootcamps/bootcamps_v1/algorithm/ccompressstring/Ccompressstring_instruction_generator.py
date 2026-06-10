import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re

# === 源文件中的全局函数 ===

def compute_min_coins(n, a_val, b_val, s):
    DP = [0] * (n + 1)
    for i in range(n):
        low = 0
        high = i + 1
        while low < high:
            mid = (low + high) // 2
            substring = s[mid:i+1]
            if substring in s[:mid]:
                high = mid
            else:
                low = mid + 1
        best_c = low
        if best_c == i + 1:
            cost_with_b = float('inf')
        else:
            cost_with_b = DP[best_c] + b_val
        cost_single = DP[i] + a_val
        DP[i+1] = min(cost_with_b, cost_single)
    return DP[n]


class CcompressstringInstructionGenerator(BaseInstructionGenerator):
    """Ccompressstring Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=5000, a_min=1, a_max=5000, b_min=1, b_max=5000):
        """
        初始化Ccompressstring指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
            b_min: 参数描述
            b_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.a_min = a_min
        self.a_max = a_max
        self.b_min = b_min
        self.b_max = b_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        a = random.randint(self.a_min, self.a_max)
        b = random.randint(self.b_min, self.b_max)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        correct_answer = compute_min_coins(n, a, b, s)
        return {
            'n': n,
            'a': a,
            'b': b,
            's': s,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = question_case['a']
        b = question_case['b']
        s = question_case['s']
        problem_description = f"""You are a string compression expert. Your task is to find the minimum number of coins required to compress a given string according to specific rules.

The rules for compression are as follows:
1. You split the string into one or more non-empty substrings t₁, t₂, ..., t_k.
2. For each substring t_i:
   - If the length of t_i is 1 (single character), it costs {a} coins.
   - If t_i is a substring of the concatenation of all previous substrings (t₁t₂…t_{{i-1}}), it costs {b} coins instead.
   - Note: A substring can be formed by deleting zero or more characters from the start and/or end of the original string. For example, "abc" has substrings like "a", "ab", "bc", "abc", etc.

You are given:
- The first line contains three integers: {n} {a} {b} (the string's length, cost for single-character substrings, cost for existing substrings).
- The second line contains the string: {s}

Your goal is to compute the minimum total coins required. Output a single integer within [answer] and [/answer] tags.

Example:
Input:
3 3 1
aba
Output:
7 (split as 'a', 'b', 'a' costing 3 + 3 + 1 = 7 coins)

Now, solve the following problem:
Input:
{n} {a} {b}
{s}

Please provide your answer as a single integer enclosed within [answer] and [/answer]."""
        return problem_description 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

