import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class CfoolsandroadsInstructionGenerator(BaseInstructionGenerator):
    """Cfoolsandroads Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10, k_min=0, k_max=10):
        """
        初始化Cfoolsandroads指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.k_min = k_min
        self.k_max = k_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        root = nodes.pop()
        edges = []
        available = [root]
        while nodes:
            u = random.choice(available)
            v = nodes.pop()
            edges.append((u, v) if random.random() < 0.5 else (v, u))
            available.append(v)
        
        random.shuffle(edges)
        
        k = random.randint(self.k_min, self.k_max)
        pairs = []
        valid_nodes = list(range(1, n+1))
        for _ in range(k):
            a, b = random.sample(valid_nodes, 2)
            pairs.append((a, b))
        
        return {
            "n": n,
            "edges": edges,
            "k": k,
            "pairs": pairs
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            str(question_case['n']),
            *[f"{u} {v}" for u, v in question_case['edges']],
            str(question_case['k']),
            *[f"{a} {b}" for a, b in question_case['pairs']]
        ]
        input_block = '\n'.join(input_lines)
        
        return f"""You are a Berland road analyst. Given a tree of cities and visiting pairs, count path usage for each road in input order.

Input format:
n
u1 v1
...
uk vk
k
a1 b1
...
ak bk

Output: space-separated integers corresponding to the roads in INPUT ORDER

Input:
{input_block}

Put your final answer within [answer] and [/answer], like:
[answer]1 2 3 4[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _find_path(cls, edges, start, end):
        adjacency = {}
        for u, v in edges:
            adjacency.setdefault(u, []).append(v)
            adjacency.setdefault(v, []).append(u)

        visited = {}
        queue = deque([start])
        visited[start] = None

        while queue:
            current = queue.popleft()
            if current == end:
                break
            for neighbor in adjacency.get(current, []):
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)

        path = []
        current = end
        while current != start and current in visited:
            parent = visited[current]
            path.append((parent, current))
            current = parent

        return path
