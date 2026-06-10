import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
import re




class CdigittreeInstructionGenerator(BaseInstructionGenerator):
    """Cdigittree Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cdigittree指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n = params.get('n', 5)
        self.M = params.get('M', 7)

        # Ensure M is coprime with 10
        if math.gcd(self.M, 10) != 1:
            while True:
                new_M = random.randint(1, 100)
                if math.gcd(new_M, 10) == 1:
                    self.M = new_M
                    break
    
    def case_generator(self):
        n = self.n
        M = self.M
        
        edges = self._generate_random_tree(n)
        adj = self._build_adjacency_list(n, edges)
        correct_answer = self._calculate_correct_answer(n, M, adj)
        
        return {
            'n': n,
            'M': M,
            'edges': edges,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        M = question_case['M']
        edges = question_case['edges']
        
        input_lines = [f"{n} {M}"]
        for u, v, w in edges:
            input_lines.append(f"{u} {v} {w}")
        input_str = '\n'.join(input_lines)
        
        return f"""ZS the Coder has a tree with {n} vertices. Each edge contains a non-zero digit. Find the number of ordered pairs (u, v) where u ≠ v and the integer formed by the path's digits is divisible by {M}.

Input:
{input_str}

Output a single integer. Place your answer within [answer] and [/answer] tags, e.g., [answer]7[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_random_tree(self, n):
        if n == 1:
            return []
        edges = []
        for i in range(1, n):
            parent = random.randint(0, i-1)
            w = random.randint(1, 9)
            edges.append((parent, i, w))
        return edges

    def _build_adjacency_list(self, n, edges):
        adj = [[] for _ in range(n)]
        for u, v, w in edges:
            adj[u].append((v, w))
            adj[v].append((u, w))
        return adj

    def _calculate_correct_answer(self, n, M, adj):
        correct = 0
        for u in range(n):
            for v in range(n):
                if u == v:
                    continue
                path = self._get_path_weights(u, v, adj)
                mod = 0
                for d in path:
                    mod = (mod * 10 + d) % M
                if mod == 0:
                    correct += 1
        return correct

    def _get_path_weights(self, u, v, adj):
        parent = {}
        visited = set([u])
        queue = [u]
        parent[u] = (None, None)
        found = False

        while queue:
            current = queue.pop(0)
            if current == v:
                found = True
                break
            for neighbor, w in adj[current]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = (current, w)
                    queue.append(neighbor)

        if not found:
            return []

        path = []
        current = v
        while current != u:
            prev, w = parent[current]
            path.append(w)
            current = prev
        path.reverse()
        return path
