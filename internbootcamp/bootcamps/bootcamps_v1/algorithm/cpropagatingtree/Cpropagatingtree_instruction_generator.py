import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的其他类 ===

class FenwickTree:
    def __init__(self, size):
        self.n = size
        self.tree = [0] * (self.n + 2)  # 1-based indexing

    def update_point(self, idx, delta):
        while idx <= self.n:
            self.tree[idx] += delta
            idx += idx & -idx

    def query_prefix(self, idx):
        res = 0
        while idx > 0:
            res += self.tree[idx]
            idx -= idx & -idx
        return res

    def update_range(self, l, r, delta):
        self.update_point(l, delta)
        self.update_point(r + 1, -delta)


class CpropagatingtreeInstructionGenerator(BaseInstructionGenerator):
    """Cpropagatingtree Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cpropagatingtree指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.m = params.get('m', 5)
        self.max_val = params.get('max_val', 1000)
        self.max_query_val = params.get('max_query_val', 1000)
    
    def case_generator(self):
        n, m = self.n, self.m
        a = [random.randint(1, self.max_val) for _ in range(n)]
        edges = self.generate_tree(n)
        queries = []
        for _ in range(m):
            if random.random() < 0.3:
                x = random.randint(1, n)
                queries.append(('2', x))
            else:
                x = random.randint(1, n)
                val = random.randint(1, self.max_query_val)
                queries.append(('1', x, val))
        
        case = {
            'n': n,
            'm': m,
            'a': a,
            'edges': edges,
            'queries': queries
        }
        expected = self.simulate_case(case)
        case['expected_outputs'] = expected
        return case
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [
            f"{question_case['n']} {question_case['m']}",
            ' '.join(map(str, question_case['a']))
        ]
        input_lines.extend(f"{u} {v}" for u, v in question_case['edges'])
        input_lines.extend(' '.join(map(str, q)) for q in question_case['queries'])
        input_str = '\n'.join(input_lines)
        return f"""Solve the propagating tree problem. Process all queries and output the results for type 2 queries. Enclose your answers within [answer] and [/answer]. Here is the input:

{input_str}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_tree(self, n):
        if n == 1:
            return []
        edges = []
        nodes = [1]
        for i in range(2, n + 1):
            parent = random.choice(nodes)
            edges.append((parent, i))
            nodes.append(i)
        return edges

    def simulate_case(self, case):
        n, a = case['n'], case['a']
        edges, queries = case['edges'], case['queries']
        tree = [[] for _ in range(n + 1)]
        for u, v in edges:
            tree[u].append(v)
            tree[v].append(u)

        # Euler Tour初始化
        euler = [-1]
        idx = [0] * (n + 1)
        child = [0] * (n + 1)
        parity = [0] * (n + 1)
        vst = [False] * (n + 1)

        def dfs(u, depth):
            vst[u] = True
            parity[u] = depth % 2
            idx[u] = len(euler)
            euler.append(u)
            child[u] = 1
            for v in tree[u]:
                if not vst[v] and v != u:
                    dfs(v, depth + 1)
                    child[u] += child[v]

        dfs(1, 0)
        max_size = len(euler) - 1

        # 初始化两个BIT
        bit0 = FenwickTree(max_size)
        bit1 = FenwickTree(max_size)
        expected = []

        # 处理查询
        for query in queries:
            if query[0] == '1':
                x = int(query[1])
                val = int(query[2])
                p = parity[x]
                L = idx[x]
                R = L + child[x] - 1  # 闭区间

                if p == 0:
                    bit0.update_range(L, R, val)
                    bit1.update_range(L, R, -val)
                else:
                    bit1.update_range(L, R, val)
                    bit0.update_range(L, R, -val)
            else:
                x = int(query[1])
                p = parity[x]
                sum_p = bit0.query_prefix(idx[x]) if p == 0 else bit1.query_prefix(idx[x])
                expected.append(a[x-1] + sum_p)
        return expected
