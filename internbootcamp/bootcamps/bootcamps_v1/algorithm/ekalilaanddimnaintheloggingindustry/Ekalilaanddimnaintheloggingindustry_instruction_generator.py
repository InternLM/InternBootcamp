import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import bisect




class EkalilaanddimnaintheloggingindustryInstructionGenerator(BaseInstructionGenerator):
    """Ekalilaanddimnaintheloggingindustry Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10):
        """
        初始化Ekalilaanddimnaintheloggingindustry指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        # Generate strictly increasing a starting with 1
        a = [1]
        for _ in range(n-1):
            delta = random.randint(1, 5)
            a.append(a[-1] + delta)
        # Generate strictly decreasing b ending with 0
        b = [0]
        for _ in range(n-1):
            delta = random.randint(1, 10)
            new_val = b[0] + delta
            b.insert(0, new_val)  # Ensure strictly decreasing
        # Compute correct answer
        correct_answer = self.__class__.compute_min_cost(n, a, b)
        return {
            "n": n,
            "a": a,
            "b": b,
            "correct_answer": correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Cut trees {question_case['a']} with costs {question_case['b']}. Minimum cost? Put answer in [answer]...[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_cost(n, a, b):
        if n == 0:
            return 0
        dp = [0] * n
        vc = []  # Convex hull trick structure (time, index)

        def saghf(x, y):
            if y < 0:
                x, y = -x, -y
            if y == 0:
                return float('inf') if x > 0 else -float('inf')
            return (x + y - 1) // y

        def when(i, j):
            return saghf(dp[i] - dp[j], b[j] - b[i])

        def add(x):
            while vc and when(vc[-1][1], x) <= vc[-1][0]:
                vc.pop()
            if not vc:
                vc.append((0, x))
            else:
                t = when(vc[-1][1], x)
                vc.append((t, x))

        def get_current(x_val):
            pos = bisect.bisect_left(vc, (x_val+1, )) - 1
            return vc[pos][1] if vc else 0

        add(0)
        for i in range(1, n):
            j = get_current(a[i])
            dp[i] = dp[j] + a[i] * b[j]
            add(i)
        return dp[-1]
