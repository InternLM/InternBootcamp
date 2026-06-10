import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class CgameontreeInstructionGenerator(BaseInstructionGenerator):
    """Cgameontree Bootcamp指令生成器"""
    
    def __init__(self, min_nodes=2, max_nodes=20):
        """
        初始化Cgameontree指令生成器
        
        Args:
            min_nodes: 参数描述
            max_nodes: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if min_nodes < 2 or max_nodes < min_nodes:
            raise ValueError("Node range must satisfy 2 ≤ min_nodes ≤ max_nodes")
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
    
    def case_generator(self):
        n = random.randint(self.min_nodes, self.max_nodes)
        edges = []
        parents = {}
        
        # Generate valid tree structure
        for node in range(2, n+1):
            parent = random.randint(1, node-1)
            parents[node] = parent
            edges.append((parent, node))

        # Build adjacency list
        adj = [[] for _ in range(n)]
        for a, b in edges:
            a_idx = a-1
            b_idx = b-1
            adj[a_idx].append(b_idx)
            adj[b_idx].append(a_idx)

        # BFS for depth calculation
        depths = [0]*n
        visited = [False]*n
        q = deque([0])  # Root node (1) has index 0
        visited[0] = True
        expectation = 0.0

        while q:
            u = q.popleft()
            expectation += 1.0 / (depths[u] + 1)  # Depth starts from 0
            
            for v in adj[u]:
                if not visited[v]:
                    visited[v] = True
                    depths[v] = depths[u] + 1
                    q.append(v)

        return {
            'n': n,
            'edges': edges,
            'expected': expectation,
            '_depth_info': depths  # For debug purposes
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges = '\n'.join(f"{a} {b}" for a, b in question_case['edges'])
        return f"""Given a rooted tree with {question_case['n']} nodes (root=1), calculate the expected number of steps to delete all nodes through random subtree removal.

Input:
{question_case['n']}
{edges}

Output requirements:
- Compute expectation with 12+ decimal places
- Enclose final answer in [answer][/answer]
- Example: [answer]2.000000000000[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

