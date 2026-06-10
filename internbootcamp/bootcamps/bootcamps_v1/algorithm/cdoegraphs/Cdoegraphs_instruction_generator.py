import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from functools import lru_cache




class CdoegraphsInstructionGenerator(BaseInstructionGenerator):
    """Cdoegraphs Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_queries=10):
        """
        初始化Cdoegraphs指令生成器
        
        Args:
            max_n: 参数描述
            max_queries: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = min(max_n, 90)  # Clamp max_n to 90 as per reference code
        self.max_queries = max_queries
    
    def case_generator(self):
        # Generate a random order n within the allowed range (1 to max_n)
        n = random.randint(1, self.max_n)
        # Compute the size of D(n) using the correct Fibonacci sequence
        fib = self.compute_doe_fib(n)
        d_size = fib[-1]
        # Generate t random valid queries
        t = random.randint(1, self.max_queries)
        queries = []
        for _ in range(t):
            a = random.randint(1, d_size)
            b = random.randint(1, d_size)
            while a == b:
                b = random.randint(1, d_size)
            a, b = sorted((a, b))
            queries.append((a, b))
        return {
            'n': n,
            'queries': queries,
            'd_size': d_size
        }
    
    @staticmethod
    def prompt_func(question_case):
        prompt = (
            "Solve the shortest path problem in a Doe graph D(n).\n"
            "Rules:\n"
            "- D(0): 1 vertex (1).\n"
            "- D(1): 2 vertices (1-2) connected.\n"
            "- D(n) for n ≥ 2 combines D(n-1) and D(n-2). Vertices in D(n-2) are renumbered by adding |D(n-1)|.\n"
            "Two new edges connect |D(n-1)| to |D(n-1)|+1 and |D(n-1)|+1 to 1.\n\n"
            f"Given D({question_case['n']}) with {len(question_case['queries'])} queries, provide the shortest path length for each pair.\n"
            "Queries:\n"
        )
        for i, (a, b) in enumerate(question_case['queries'], 1):
            prompt += f"{i}. {a} ↔ {b}\n"
        prompt += (
            "\nEnclose answers within [answer] tags, each on separate lines.\n"
            "Example:\n[answer]\n3\n2\n5\n[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_doe_fib(n):
        """Generates the Fibonacci sequence for Doe graph sizes up to order n (0-based)."""
        if n < 0:
            return []
        fib = [1]  # D(0)
        if n == 0:
            return fib
        fib.append(2)  # D(1)
        for i in range(2, n + 1):
            fib.append(fib[i-1] + fib[i-2])
        return fib

    @classmethod
    def dfs(cls, a, b, k, fib_tuple):
        if a == b:
            return 0
        if k == 1:
            return 1
        if a > b:
            a, b = b, a
        return cls._dfs(a, b, k, fib_tuple)

    @classmethod
    def _dfs(cls, a, b, k, fib_tuple):
        if a == b:
            return 0
        if k == 1:
            return 1
        if k == 0:
            return 0

        size_k_1 = fib_tuple[k-1]
        if a > size_k_1 and b > size_k_1:
            return cls._dfs(a - size_k_1, b - size_k_1, k-2, fib_tuple)
        if a <= size_k_1 and b <= size_k_1:
            path_in = cls._dfs(a, b, k-1, fib_tuple)
            path1 = cls.dfs1(k-1, 0, a, fib_tuple) + cls.dfs2(k-1, 1, b, fib_tuple) + 2
            path2 = cls.dfs1(k-1, 1, a, fib_tuple) + cls.dfs2(k-1, 0, b, fib_tuple) + 2
            return min(path_in, path1, path2)
        else:
            path1 = min(cls.dfs1(k-1, 0, a, fib_tuple), cls.dfs1(k-1, 1, a, fib_tuple))
            path2 = cls.dfs2(k-2, 0, b - size_k_1, fib_tuple) + 1
            return path1 + path2

    @classmethod
    @lru_cache(maxsize=None)
    def dfs1(cls, a, b, c, fib_tuple):
        if a == 1:
            return 1 if (c + b) == 2 else 0
        if a == 0:
            return 0
        size_a_1 = fib_tuple[a-1]
        if b:
            if c > size_a_1:
                return cls.dfs1(a-2, 1, c - size_a_1, fib_tuple)
            else:
                option1 = cls.dfs1(a-1, 1, c, fib_tuple)
                option2 = cls.dfs1(a-1, 0, c, fib_tuple)
                return min(option1, option2) + 1 + (a-1) // 2
        else:
            if c > size_a_1:
                return cls.dfs1(a-2, 0, c - size_a_1, fib_tuple) + 1
            else:
                option1 = cls.dfs1(a-1, 0, c, fib_tuple)
                option2 = cls.dfs1(a-1, 1, c, fib_tuple) + 2
                return min(option1, option2)

    @classmethod
    @lru_cache(maxsize=None)
    def dfs2(cls, a, b, c, fib_tuple):
        if a == 1:
            return 1 if (c + b) == 2 else 0
        if a == 0:
            return 0
        size_a_1 = fib_tuple[a-1]
        if b:
            if c > size_a_1:
                return cls.dfs2(a-2, 1, c - size_a_1, fib_tuple)
            else:
                option1 = cls.dfs2(a-1, 1, c, fib_tuple)
                option2 = cls.dfs2(a-1, 0, c, fib_tuple)
                return min(option1, option2) + 1 + (a-1) // 2
        else:
            if c > size_a_1:
                return cls.dfs2(a-2, 0, c - size_a_1, fib_tuple) + 1
            else:
                option1 = cls.dfs2(a-1, 0, c, fib_tuple)
                option2 = cls.dfs2(a-1, 1, c, fib_tuple) + 2
                return min(option1, option2)
