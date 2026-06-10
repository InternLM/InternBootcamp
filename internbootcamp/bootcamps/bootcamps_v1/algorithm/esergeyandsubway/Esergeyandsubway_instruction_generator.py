import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class EsergeyandsubwayInstructionGenerator(BaseInstructionGenerator):
    """Esergeyandsubway Bootcamp指令生成器"""
    
    def __init__(self, max_n=100):
        """
        初始化Esergeyandsubway指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，设置生成树的最大节点数。
        """
        self.max_n = max_n
        self.min_n = 2
    
    def case_generator(self):
        """
        生成一个树结构实例，并计算正确的答案。
        """
        n = random.randint(self.min_n, self.max_n)
        edges = self.generate_random_tree(n)
        correct_answer = self.solve(n, edges)
        return {
            'n': n,
            'edges': edges,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        edges = question_case['edges']
        n = question_case['n']
        edges_str = '\n'.join(f"{u} {v}" for u, v in edges)
        prompt = f"""Sergey Semyonovich, the mayor of city N, wants to improve the subway system. The subway network is a tree with {n} stations. Sergey adds new tunnels between any two stations u and v that were not directly connected but share a common neighbor. Your task is to calculate the sum of all pairwise distances between stations after these new tunnels are added.

Input:
The first line contains an integer n (2 ≤ n ≤ 200000) — the number of stations. The next n-1 lines describe the tunnels, each with two integers u and v.

Problem instance:
n = {n}
The tunnels are:
{edges_str}

Your answer must be a single integer. Please place your final answer within [answer] and [/answer] tags. For example, [answer]42[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_random_tree(n):
        """
        使用Prüfer序列生成随机树。
        """
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]

        prufer = [random.randint(1, n) for _ in range(n-2)]
        degree = [0] * (n + 1)
        for node in prufer:
            degree[node] += 1

        leaves = []
        for i in range(1, n + 1):
            if degree[i] == 0:
                leaves.append(i)

        edges = []
        for node in prufer:
            leaf = leaves.pop(0)
            edges.append((leaf, node))
            degree[node] -= 1
            if degree[node] == 0:
                leaves.append(node)
            leaves.sort()

        edges.append((leaves[0], leaves[1]))
        return edges

    @staticmethod
    def solve(n, edges_list):
        """
        根据给定的树结构计算正确的结果。
        """
        adj = [[] for _ in range(n+1)]
        for a, b in edges_list:
            adj[a].append(b)
            adj[b].append(a)

        root = 1
        q = [root]
        odd = [0] * (n+1)
        even = [0] * (n+1)
        odd_size = [0] * (n+1)
        even_size = [1] * (n+1)
        rank = [0] * (n+1)
        rank[root] = 1

        i = 0
        while i < len(q):
            node = q[i]
            for v in adj[node]:
                if rank[v] == 0:
                    rank[v] = rank[node] + 1
                    q.append(v)
            i += 1

        for node in reversed(q):
            for v in adj[node]:
                if rank[v] > rank[node]:
                    odd[node] += even[v] + even_size[v]
                    even[node] += odd[v] + odd_size[v]
                    even_size[node] += odd_size[v]
                    odd_size[node] += even_size[v]

        for node in q:
            for v in adj[node]:
                if rank[v] > rank[node]:
                    deven = odd[node] - (even[v] + even_size[v]) + (odd_size[node] - even_size[v])
                    dodd = even[node] - (odd[v] + odd_size[v]) + (even_size[node] - odd_size[v])
                    even[v] += deven
                    odd[v] += dodd
                    even_size[v] = odd_size[node]
                    odd_size[v] = even_size[node]

        ans = 0
        for i in range(1, n+1):
            ans += even[i] // 2
            ans += (odd[i] + odd_size[i]) // 2
        ans = ans // 2
        return ans
