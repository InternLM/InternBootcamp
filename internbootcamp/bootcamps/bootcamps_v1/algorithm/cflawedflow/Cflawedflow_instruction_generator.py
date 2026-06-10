import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque

# === 源文件中的其他类 ===

class Edge:
    def __init__(self, from_, to_, w_, id_):
        self.from_ = from_
        self.to_ = to_
        self.w_ = w_
        self.id_ = id_


class CflawedflowInstructionGenerator(BaseInstructionGenerator):
    """Cflawedflow Bootcamp指令生成器"""
    
    def __init__(self, max_n=8, max_m=15):
        """
        初始化Cflawedflow指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(2, self.max_n)
        max_edges = n * (n - 1) // 2
        m = random.randint(n-1, min(max_edges, self.max_m))
        edges = self._generate_connected_edges(n, m)
        solution = self._generate_solution(n, edges)
        return {
            "n": n,
            "m": m,
            "edges": edges,
            "solution": solution
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges = question_case["edges"]
        n = question_case["n"]
        m = question_case["m"]
        edge_lines = "\n".join([f"{a} {b} {c}" for a, b, c in edges])
        return f"""作为流量算法专家，请确定无向图中各边方向，并遵守以下规则：
1. 源点（1号顶点）没有入边
2. 中间节点（非源点和汇点）流入等于流出
3. 最终图必须无环

输入格式：
{n} {m}
{edge_lines}

请输出{m}个0或1（对应每条边的方向），答案用[answer]标签包裹，如：
[answer]
0 1 1 0
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_connected_edges(n, m):
        parent = list(range(n+1))

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        edges = []
        existing = set()

        # Generate spanning tree to ensure connectivity
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        root = nodes[0]
        for node in nodes[1:]:
            a, b = root, node
            if a > b:
                a, b = b, a
            c = random.randint(1, 10000)
            edges.append((a, b, c))
            existing.add((a, b))
            parent[b] = a

        # Add remaining edges
        remaining = m - (n-1)
        candidates = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1) if (i, j) not in existing]
        while remaining > 0 and candidates:
            add_num = min(remaining, len(candidates))
            selected = random.sample(candidates, add_num)
            for a, b in selected:
                c = random.randint(1, 10000)
                edges.append((a, b, c))
                existing.add((a, b))
                candidates.remove((a, b))  # Prevent duplicate selection
            remaining -= add_num

        random.shuffle(edges)
        return edges[:m]

    @staticmethod
    def _generate_solution(n, edges):
        m = len(edges)
        graph = [[] for _ in range(n+1)]
        wall = [0]*(n+1)
        for idx, (a, b, c) in enumerate(edges):
            edge = Edge(a, b, c, idx)
            graph[a].append(edge)
            graph[b].append(edge)
            wall[a] += c
            wall[b] += c

        ans = [-1]*m
        win = [0]*(n+1)
        q = deque([1])

        while q:
            u = q.popleft()
            to_check = []
            for edge in graph[u]:
                if ans[edge.id_] != -1:
                    continue
                if edge.from_ == u:
                    v = edge.to_
                    ans[edge.id_] = 0
                else:
                    v = edge.from_
                    ans[edge.id_] = 1
                win[v] += edge.w_
                wall[v] -= edge.w_
                if v != n:
                    to_check.append(v)

            for v in to_check:
                if win[v] == wall[v]:
                    q.append(v)

        return ans
