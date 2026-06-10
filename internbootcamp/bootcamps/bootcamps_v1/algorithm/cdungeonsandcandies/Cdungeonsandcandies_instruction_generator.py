import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CdungeonsandcandiesInstructionGenerator(BaseInstructionGenerator):
    """Cdungeonsandcandies Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cdungeonsandcandies指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', random.randint(1, 10))
        self.m = params.get('m', random.randint(1, 10))
        self.k = params.get('k', random.randint(1, 5))
        self.w = params.get('w', random.randint(1, 1000))
    
    def case_generator(self):
        levels = []
        for _ in range(self.k):
            level = [''.join(random.choices(
                ['.', 'A', 'B', 'C', 'a', 'b', 'c', 'X', 'Y', 'Z'], k=self.m
            )) for _ in range(self.n)]
            levels.append(level)
        
        correct_total = self._compute_min_traffic(self.n, self.m, self.k, self.w, levels)
        return {
            'n': self.n,
            'm': self.m,
            'k': self.k,
            'w': self.w,
            'levels': levels,
            'correct_total': correct_total
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        levels = '\n\n'.join([f"Level {i+1}:\n" + '\n'.join(level) 
                            for i, level in enumerate(question_case['levels'])])
        return f"""You are optimizing data transfer for the game "Dungeons and Candies". Transmit {question_case['k']} {question_case['n']}x{question_case['m']} grids with minimal traffic. Each cell contains '.' or a letter (case-sensitive).

Rules:
1. Transmit full level ({question_case['n']*question_case['m']} bytes) or difference from a previous level (d*{question_case['w']} bytes, d=differing cells).
2. Levels can be transmitted in any order.

Output format:
- First line: Total bytes
- Next {question_case['k']} lines: "xi yi" (xi=level number, yi=0 or previous level)

Examples:
[answer]
14
1 0
2 1
3 1
[/answer]

Provide your answer within [answer] tags. Current levels:
{levels}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_min_traffic(n, m, k, w, levels):
        def dif(a, b):
            return sum(c1 != c2 for row_a, row_b in zip(a, b) for c1, c2 in zip(row_a, row_b))

        edges = []
        for i in range(k):
            for j in range(i+1, k):
                cost = dif(levels[i], levels[j]) * w
                if cost < n * m:
                    edges.append((i, j, cost))
        edges.sort(key=lambda x: x[2])

        parent = list(range(k))
        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        def union(u, v):
            u_root, v_root = find(u), find(v)
            if u_root != v_root:
                if random.choice([True, False]):
                    parent[u_root] = v_root
                else:
                    parent[v_root] = u_root

        mst_cost = 0
        for u, v, cost in edges:
            if find(u) != find(v):
                mst_cost += cost
                union(u, v)

        roots = {find(x) for x in range(k)}
        return mst_cost + len(roots) * n * m
