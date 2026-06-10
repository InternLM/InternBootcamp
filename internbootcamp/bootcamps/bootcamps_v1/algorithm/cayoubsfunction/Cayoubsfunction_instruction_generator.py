import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CayoubsfunctionInstructionGenerator(BaseInstructionGenerator):
    """Cayoubsfunction Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10**9):
        """
        初始化Cayoubsfunction指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        支持极大数值范围的初始化参数
        参数:
            n_min: 可生成的最小n值 (default=1)
            n_max: 可生成的最大n值 (default=1e9)
        """
        self.n_min = n_min
        self.n_max = n_max
    
    def case_generator(self):
        # 30%生成特殊边界情况
        if random.random() < 0.3:
            n = random.randint(self.n_min, self.n_max)
            special_cases = [
                (n, 0),         # 全0字符串
                (n, n),         # 全1字符串
                (n, n//2),      # 临界值情况
                (n, n//2 + 1)   # 临界值+1
            ]
            return dict(zip(['n', 'm'], random.choice(special_cases)))
        
        # 常规随机生成
        n = random.randint(max(1, self.n_min), self.n_max)
        m = random.randint(0, n)
        return {"n": n, "m": m}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        return f"""### Programming Problem Statement

Given a binary string s of length {n} containing exactly {m} '1's, find the maximum possible value of function f(s). 

**Function Definition:**
f(s) = number of substrings containing at least one '1'

**Substring Definition:**
A substring is any contiguous sequence of characters from index l to r (1 ≤ l ≤ r ≤ n)

**Examples:**
1. Input: n=3, m=1 → Output:4
2. Input: n=5, m=2 → Output:12
3. Input: n=4, m=0 → Output:0

**Your Task:**
Compute the maximum f(s) for n={n}, m={m}. 

**Answer Format Requirements:**
- Return only the integer answer 
- Enclose your final answer with [answer] and [/answer] tags
- Example valid response: [answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answer(n, m):
        """参考计算方法（用于生成测试答案）"""
        if m == 0:
            return 0
        total = n * (n + 1) // 2
        if m >= n / 2.0:
            return total - (n - m)

        c = m + 1
        z = n - m
        base, rem = divmod(z, c)
        return total - (
            rem * (base + 1) * (base + 2) // 2 +
            (c - rem) * base * (base + 1) // 2
        )
