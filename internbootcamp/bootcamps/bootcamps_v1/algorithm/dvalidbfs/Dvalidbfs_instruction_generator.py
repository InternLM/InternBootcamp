import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque




class DvalidbfsInstructionGenerator(BaseInstructionGenerator):
    """Dvalidbfs Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dvalidbfs指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 4)
    
    def case_generator(self):
        n = self.n
        if n == 1:
            case = {
                'n': 1,
                'edges': [],
                'sequence': [1]
            }
            return case
        
        edges = []
        visited = [False] * (n + 1)
        q = deque([1])
        visited[1] = True
        
        while q:
            u = q.popleft()
            possible_neighbors = [i for i in range(1, n + 1) if not visited[i] and i != u]
            if possible_neighbors:
                v = random.choice(possible_neighbors)
                edges.append((u, v))
                visited[v] = True
                q.append(v)
        
        while len(edges) < n - 1:
            u = random.randint(1, n)
            v = random.randint(1, n)
            if u != v and (u, v) not in edges and (v, u) not in edges:
                edges.append((u, v))
        
        adj = [[] for _ in range(n + 1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        for i in range(1, n + 1):
            adj[i].sort()
        
        visited = [False] * (n + 1)
        q = deque([1])
        visited[1] = True
        correct_order = []
        while q:
            v = q.popleft()
            correct_order.append(v)
            for u in adj[v]:
                if not visited[u]:
                    visited[u] = True
                    q.append(u)
        
        wrong_order = correct_order.copy()
        if len(wrong_order) >= 2:
            pos1, pos2 = random.sample(range(1, len(wrong_order)), 2)
            wrong_order[pos1], wrong_order[pos2] = wrong_order[pos2], wrong_order[pos1]
        
        if random.random() < 0.5:
            sequence = correct_order
        else:
            sequence = wrong_order
        
        case = {
            'n': n,
            'edges': edges,
            'sequence': sequence
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        sequence = question_case['sequence']
        prompt = f"Consider a tree with {n} nodes. The edges are as follows:\n"
        for u, v in edges:
            prompt += f"{u} {v}\n"
        prompt += f"Given the sequence: {sequence}\n"
        prompt += "Determine if this sequence is a valid BFS traversal starting from node 1. Output 'Yes' if it is valid, 'No' otherwise.\n"
        prompt += "Please provide your answer within [answer] tags.\n"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

