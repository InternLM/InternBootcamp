import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CannasvyatoslavandmapsInstructionGenerator(BaseInstructionGenerator):
    """Cannasvyatoslavandmaps Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cannasvyatoslavandmaps指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
        self.params.setdefault('n_min', 2)
        self.params.setdefault('n_max', 10)
        self.params.setdefault('m_min', 2)
        self.params.setdefault('m_max', 20)
    
    def case_generator(self):
        n = random.randint(self.params['n_min'], self.params['n_max'])
        m = random.randint(self.params['m_min'], self.params['m_max'])
        
        # Generate valid path with guaranteed edges
        p = []
        current = random.randint(1, n)
        p.append(current)
        adj_matrix = [[0]*n for _ in range(n)]
        
        for _ in range(m-1):
            available = [v for v in range(1, n+1) if v != current]
            next_v = random.choice(available)
            adj_matrix[current-1][next_v-1] = 1  # Mark existing edge
            p.append(next_v)
            current = next_v

        # Fill remaining edges (avoid self loops)
        for u in range(n):
            for v in range(n):
                if u != v and adj_matrix[u][v] == 0:
                    adj_matrix[u][v] = random.choice([0, 1])

        return {
            'n': n,
            'adj_matrix': [''.join(map(str, row)) for row in adj_matrix],
            'm': m,
            'p': p
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        adj_matrix = question_case['adj_matrix']
        m = question_case['m']
        p_str = ' '.join(map(str, question_case['p']))
        
        return f"""You are given a directed graph with {n} vertices and a path. Find the shortest good subsequence.

Graph adjacency matrix:
"""+'\n'.join(adj_matrix)+f"""

Path ({m} vertices):
{p_str}

A good subsequence must:
1. Be a subsequence starting and ending with path's first/last vertex
2. Original path must be the shortest path for this subsequence

Output format:
[answer]
k
v1 v2 ... vk
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

