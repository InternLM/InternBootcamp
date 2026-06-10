import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CmaximandmatrixInstructionGenerator(BaseInstructionGenerator):
    """Cmaximandmatrix Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cmaximandmatrix指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
    
    def case_generator(self):
        max_n = 10**12
        # 简化生成逻辑确保数值在合法范围
        n = random.randint(1, max_n)
        t_max = min(n + 1, 10**12)
        t = random.randint(1, t_max)
        return {"n": n, "t": t}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["n"]
        t = question_case["t"]
        prompt = (
            "Maxim loves to fill a matrix in a special way. Given two integers n and t, your task is to count how many integers m (1 ≤ m ≤ n) satisfy the following condition: The sum of values in the (m+1)th row (1-based) of the matrix equals t.\n\n"
            "Matrix Construction Rules:\n"
            "- The matrix is of size (m+1) × (m+1), where rows and columns are 0-based.\n"
            "- Each cell at row i and column j contains the value (i XOR j).\n\n"
            "Input Constraints:\n"
            f"- 1 ≤ n, t ≤ 10^12\n"
            f"- t ≤ n + 1\n\n"
            "Your task is to compute the number of valid m values. Provide your answer as an integer enclosed within [answer] and [/answer] tags.\n\n"
            "Example:\n"
            "Input: 1 1\n"
            "Output: [answer]1[/answer]\n\n"
            f"Now, solve for n = {n} and t = {t}. Place your final answer within [answer] tags."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _build_c(cls):
        if cls._c is not None:
            return
        c = []
        c.append([1])
        for i in range(1, 60):
            q = [1]
            for j in range(1, i):
                q.append(c[i-1][j] + c[i-1][j-1])
            q.append(1)
            c.append(q)
        cls._c = c

    @classmethod
    def f(cls, n, t):
        cls._build_c()
        if n == 0 and t == 0:
            return 1
        if t < 0:
            return 0
        x = 0
        while (2 ** x) <= n:
            x += 1
        x -= 1
        max_k = x
        if (t + 1) <= max_k:
            ans = cls._c[x][t + 1]
        else:
            ans = 0
        remaining = n - (2 ** x)
        if remaining > 0 and t > 0:
            ans += cls.f(remaining, t - 1)
            if t == 1:
                ans += 1
        return ans
