import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import sys




class CworldeaterbrothersInstructionGenerator(BaseInstructionGenerator):
    """Cworldeaterbrothers Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Cworldeaterbrothers指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        n = self.n
        if n < 1:
            raise ValueError("n must be at least 1")
        
        if n == 1:
            edges = []
            correct_answer = 0
        else:
            undirected_edges = self.generate_tree(n)
            directed_edges = []
            for u, v in undirected_edges:
                if random.choice([True, False]):
                    directed_edges.append([u + 1, v + 1])
                else:
                    directed_edges.append([v + 1, u + 1])
            
            adj = [[] for _ in range(n)]
            for ai, bi in directed_edges:
                x = ai - 1
                y = bi - 1
                adj[x].append((y, 1))
                adj[y].append((x, 0))
            
            correct_answer = self.compute_answer(n, adj)
        
        return {
            "n": n,
            "edges": directed_edges if n > 1 else [],
            "correct_answer": correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges = question_case['edges']
        edges_str = "\n".join(f"{a} {b}" for a, b in edges)
        prompt = f"""The world consists of {question_case['n']} countries connected by {question_case['n']-1} directed roads, forming a tree when directions are ignored. Two brothers want to choose up to two countries such that every other country is reachable from at least one of them via directed roads. Find the minimum number of road reversals needed.

Input:
{question_case['n']}
{edges_str if edges else ''}

Please provide your answer as an integer enclosed within [answer] and [/answer] tags. For example: [answer]5[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_tree(n):
        if n == 1:
            return []
        parents = [random.randint(0, i-1) for i in range(1, n)]
        edges = []
        for i in range(1, n):
            parent = parents[i-1]
            edges.append((parent, i))
        return edges

    @staticmethod
    def compute_answer(n, adj):
        if n == 1:
            return 0

        dp = [0] * n
        ans = n - 1

        def dfs1(v, p):
            for u, f in adj[v]:
                if u == p:
                    continue
                dfs1(u, v)
                dp[v] += dp[u] + (1 - f)

        dfs1(0, -1)

        def dfs2(v, p):
            for u, f in adj[v]:
                if u == p:
                    continue
                dp[u] = dp[v] + (1 if f else -1)
                dfs2(u, v)

        dfs2(0, -1)

        def dfs3(v, p):
            m1, m2 = 0, 0
            for u, f in adj[v]:
                if u == p:
                    continue
                cm1, cm2 = dfs3(u, v)
                current = cm1 + (0 if f else 1)
                if current >= m1:
                    m2 = m1
                    m1 = current
                elif current > m2:
                    m2 = current
            return (m1, m2)

        for i in range(n):
            mx1, mx2 = dfs3(i, -1)
            current_ans = dp[i] - mx1 - mx2
            ans = min(ans, current_ans)

        return ans
