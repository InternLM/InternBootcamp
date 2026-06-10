import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from functools import lru_cache
import re




class EdoegraphsInstructionGenerator(BaseInstructionGenerator):
    """Edoegraphs Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_queries=10):
        """
        初始化Edoegraphs指令生成器
        
        Args:
            max_n: 参数描述
            max_queries: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_queries = max_queries
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        self._ensure_f(n)
        fn = self._f[n]
        queries = []
        for _ in range(self.max_queries):
            a = random.randint(1, fn)
            b = random.randint(1, fn)
            while a == b:
                b = random.randint(1, fn)
            queries.append((a, b))
        return {'n': n, 'queries': queries, 'f_n': fn}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        queries = question_case['queries']
        prompt = f"""你是图论专家，请解决以下Doe图的最短路径问题。

Doe图D(k)根据其阶数k构建。D(0)是单个顶点1；D(1)是两个顶点1和2的边。对于k≥2，D(k)由D(k-1)和D(k-2)合并，并添加两条边连接他们的顶点。每个顶点都有唯一的编号。

给定阶数为{n}的Doe图D({n})，顶点数目为{question_case['f_n']}。现有{len(queries)}个查询，每个查询要求计算两个不同顶点之间的最短路径长度。

输入格式：每个查询给出两个顶点编号a_i和b_i。

输出格式：对于每个查询，输出一个整数，表示最短路径的长度。

请按顺序对每个查询给出答案，每个答案占一行，并将所有答案放在[answer]和[/answer]之间。

例如，对于两个查询的输出应为：

[answer]
3
5
[/answer]

现在，处理以下查询：
"""
        for i, (a, b) in enumerate(queries, 1):
            prompt += f"查询{i}: {a} {b}\n"
        prompt += "\n请按要求输出答案。"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _ensure_f(cls, n):
        while len(cls._f) <= n:
            next_val = cls._f[-1] + cls._f[-2]
            cls._f.append(next_val)

    @staticmethod
    @lru_cache(maxsize=None)
    def compute_shortest_path(a, b, n):
        if a == b:
            return 0
        if a > b:
            a, b = b, a
        if n == 0:
            return 0
        if n == 1:
            return 1

        Edoegraphsbootcamp._ensure_f(n - 1)
        fn_minus_1 = Edoegraphsbootcamp._f[n - 1]
        a_in_B = a > fn_minus_1
        b_in_B = b > fn_minus_1

        if a_in_B and b_in_B:
            new_a = a - fn_minus_1
            new_b = b - fn_minus_1
            return Edoegraphsbootcamp.compute_shortest_path(new_a, new_b, n - 2)
        elif b_in_B:
            part_b = Edoegraphsbootcamp.compute_shortest_path(1, b - fn_minus_1, n - 2)
            option1 = Edoegraphsbootcamp.compute_shortest_path(a, fn_minus_1, n - 1)
            option2 = Edoegraphsbootcamp.compute_shortest_path(a, 1, n - 1)
            part_a = min(option1, option2)
            return part_a + part_b + 1
        else:
            option1 = Edoegraphsbootcamp.compute_shortest_path(a, b, n - 1)
            optionA = Edoegraphsbootcamp.compute_shortest_path(a, fn_minus_1, n - 1) + \
                      Edoegraphsbootcamp.compute_shortest_path(1, b, n - 1) + 2
            optionB = Edoegraphsbootcamp.compute_shortest_path(a, 1, n - 1) + \
                      Edoegraphsbootcamp.compute_shortest_path(fn_minus_1, b, n - 1) + 2
            option2 = min(optionA, optionB)
            return min(option1, option2)
