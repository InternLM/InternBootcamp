import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class ClinkcutcentroidsInstructionGenerator(BaseInstructionGenerator):
    """Clinkcutcentroids Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=20):
        """
        初始化Clinkcutcentroids指令生成器
        
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
        if n == 1:
            return {'n': 1, 'edges': []}
        if n == 2:
            return {'n': 2, 'edges': [(1, 2)]}

        # 使用改进的Prüfer序列生成器
        prufer = [random.randint(1, n) for _ in range(n-2)]
        degree = [1] * (n+1)
        for node in prufer:
            degree[node] += 1

        edges = []
        ptr = 1
        while degree[ptr] != 1:
            ptr += 1
        leaf = ptr

        for node in prufer:
            edges.append((leaf, node))
            degree[leaf] -= 1
            degree[node] -= 1
            if degree[node] == 1 and node < ptr:
                leaf = node
            else:
                ptr += 1
                while ptr <= n and degree[ptr] != 1:
                    ptr += 1
                leaf = ptr

        edges.append((leaf, next(i for i in range(1, n+1) if degree[i] == 1 and i != leaf)))
        return {'n': n, 'edges': [(min(u,v), max(u,v)) for u,v in edges]}
    
    @staticmethod
    def prompt_func(question_case):
        edges = question_case['edges']
        n = question_case['n']
        edges_str = "\n".join(f"{u} {v}" for u, v in edges)
        return f"""Given a tree with {n} vertices connected by these edges:
{edges_str}

Find an edge to cut and an edge to add so that the resulting tree has exactly one centroid. Format your answer as:

[answer]
cut_u cut_v
add_u add_v
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def find_centroids(n, adj):
        subtree = [0]*(n+1)

        def dfs(u, parent):
            subtree[u] = 1
            for v in adj[u]:
                if v != parent:
                    dfs(v, u)
                    subtree[u] += subtree[v]

        dfs(1, -1)  # Root at node 1

        centroids = []
        min_max = float('inf')
        for u in range(1, n+1):
            max_size = max(
                (n - subtree[u], 
                 max((subtree[v] for v in adj[u] if v != parent), default=0))
                for parent in [-1]  # Simplified check
            )[0]
            if max_size < min_max:
                min_max = max_size
                centroids = [u]
            elif max_size == min_max:
                centroids.append(u)
        return list(set(centroids))
