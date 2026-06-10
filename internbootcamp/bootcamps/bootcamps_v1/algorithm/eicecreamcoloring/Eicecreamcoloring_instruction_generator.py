import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class EicecreamcoloringInstructionGenerator(BaseInstructionGenerator):
    """Eicecreamcoloring Bootcamp指令生成器"""
    
    def __init__(self, n=10, m=10, max_si=5):
        """
        初始化Eicecreamcoloring指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            max_si: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
        self.max_si = max_si
        self.tree_edges = []
        self.node_types = defaultdict(list)
        self.g_edges = set()
    
    def case_generator(self):
        # Generate a tree structure
        self.tree_edges = []
        # Create a more complex tree structure
        parent = [i for i in range(self.n)]
        for i in range(1, self.n):
            # Choose a random parent for node i+1
            p = random.randint(1, i)
            self.tree_edges.append((p, i+1))
        
        # Assign each type to a node ensuring connected subgraph
        self.node_types = defaultdict(list)
        for type_id in range(1, self.m+1):
            # Choose a root node randomly
            root = random.randint(1, self.n)
            # Perform BFS to select a connected subset
            visited = set()
            queue = [root]
            visited.add(root)
            while queue and random.random() < 0.7:  # Control the size of the subset
                current = queue.pop(0)
                self.node_types[current].append(type_id)
                # Add neighbors to queue
                for neighbor in self.get_neighbors(current):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append(neighbor)
        
        # Build the graph G
        self.g_edges = set()
        for node in self.node_types.values():
            # Generate all pairs of types in this node
            for i in range(len(node)):
                for j in range(i+1, len(node)):
                    u, v = node[i], node[j]
                    if u < v:
                        self.g_edges.add((u, v))
                    else:
                        self.g_edges.add((v, u))
        
        # Construct the problem case
        case = {
            'n': self.n,
            'm': self.m,
            'node_types': {k: v for k, v in self.node_types.items()},
            'tree_edges': self.tree_edges,
            'g_edges': list(self.g_edges)
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        prompt = (
            "We have a tree T with {} vertices and {} types of ice cream. Each vertex contains certain types of ice cream as follows:\n"
            "Vertex Types:\n"
        ).format(question_case['n'], question_case['m'])
        
        for node, types in question_case['node_types'].items():
            prompt += f"Vertex {node}: {types}\n"
        
        prompt += (
            "The tree T has the following edges:\n"
            "Tree Edges:\n"
        )
        for u, v in question_case['tree_edges']:
            prompt += f"{u} {v}\n"
        
        prompt += (
            "We need to construct a graph G where each vertex represents an ice cream type. There is an edge between two types if they appear together in at least one vertex of T.\n"
            "The task is to color the vertices of G using the minimum number of colors such that no two adjacent vertices share the same color.\n"
            "Please provide the minimum number of colors and the color assignment for each type. The colors should be integers starting from 1.\n"
            "Format your answer as follows:\n"
            "[answer]\n"
            "c\n"
            "c1 c2 c3 ... cm\n"
            "[/answer]\n"
        )
        
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def get_neighbors(self, node):
        # Helper function to get neighbors of a node in the tree
        neighbors = []
        for u, v in self.tree_edges:
            if u == node:
                neighbors.append(v)
            if v == node:
                neighbors.append(u)
        return neighbors
