import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def is_balanced(s):
    balance = 0
    for char in s:
        if char == '(':
            balance += 1
        else:
            balance -= 1
        if balance < 0:
            return False
    return balance == 0

def count_regular_prefixes(s):
    count = 0
    balance = 0
    for i in range(len(s)):
        char = s[i]
        balance += 1 if char == '(' else -1
        if balance < 0:
            break
        if balance == 0:
            count += 1
    return count

def generate_s_final(n, k):
    if k == 0:
        return ''
    prefix = "()" * (k - 1)
    remaining = n - 2 * (k - 1)
    m = remaining // 2
    suffix = '(' * m + ')' * m
    return prefix + suffix


class CmessyInstructionGenerator(BaseInstructionGenerator):
    """Cmessy Bootcamp指令生成器"""
    
    def __init__(self, n=None, k=None, min_n=2, max_n=2000):
        """
        初始化Cmessy指令生成器
        
        Args:
            n: 参数描述
            k: 参数描述
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.k = k
        self.min_n = max(2, min_n)
        self.max_n = min(2000, max_n)
        if self.n is not None:
            assert self.n % 2 == 0, "n must be even"
            assert self.min_n <= self.n <= self.max_n, "n out of allowed range"
    
    def case_generator(self):
        if self.n is not None:
            n = self.n
        else:
            possible_n = list(range(self.min_n, self.max_n + 1, 2))
            n = random.choice(possible_n)
        
        max_k = n // 2
        if self.k is not None:
            k = self.k
            assert 1 <= k <= max_k, f"k must be between 1 and {max_k}"
        else:
            k = random.randint(1, max_k)
        
        s_final = generate_s_final(n, k)
        
        m_ops = random.randint(0, n)
        ops = []
        initial_s = s_final
        for _ in range(m_ops):
            l = random.randint(1, n)
            r = random.randint(l, n)
            ops.append((l, r))
            l_idx = l - 1
            r_idx = r
            substring = initial_s[l_idx:r_idx]
            reversed_sub = substring[::-1]
            initial_s = initial_s[:l_idx] + reversed_sub + initial_s[r_idx:]
        
        return {
            "n": n,
            "k": k,
            "s": initial_s,
            "original_ops": ops  # Storing for potential verification, though not used in normal flow
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        s = question_case['s']
        problem = f"""You are tasked with cleaning up a messy bracket sequence to meet specific criteria. 

The current sequence is:

**Input:**
- Length n = {n}
- Target number of regular prefixes k = {k}
- Initial sequence: {s}

**Operations Allowed:** You can reverse any consecutive substring of the sequence. Each reversal counts as one operation. You can perform at most {n} operations.

**Goals:**
1. The final sequence must be a **regular bracket sequence** (balanced and valid).
2. The final sequence must have exactly **{k} regular prefixes** (including the entire sequence).

**Output Format:**
Provide the number of operations followed by each operation's indices (1-based). Enclose your answer within [answer] and [/answer] tags.

Example format:
[answer]
3
4 10
1 4
6 7
[/answer]

Now, determine the required operations to achieve the goal."""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

