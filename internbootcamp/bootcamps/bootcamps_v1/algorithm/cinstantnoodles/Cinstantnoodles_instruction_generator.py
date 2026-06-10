import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import math
import random
from collections import defaultdict




class CinstantnoodlesInstructionGenerator(BaseInstructionGenerator):
    """Cinstantnoodles Bootcamp指令生成器"""
    
    def __init__(self, max_n_left=5, max_k=5, max_m=20, **params):
        """
        初始化Cinstantnoodles指令生成器
        
        Args:
            max_n_left: 参数描述
            max_k: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n_left = max_n_left
        self.max_k = max_k
        self.max_m = max_m
        self.params = params
    
    def case_generator(self):
        n_left = random.randint(1, self.max_n_left)
        k = random.randint(1, self.max_k)
        max_possible_edges = n_left * k
        m = random.randint(1, min(self.max_m, max_possible_edges))
        
        c = [random.randint(1, 100) for _ in range(k)]
        
        edges_set = set()
        edges = []
        possible_edges = [(u, v) for u in range(1, n_left+1) for v in range(1, k+1)]
        random.shuffle(possible_edges)
        possible_edges = possible_edges[:m]
        for edge in possible_edges:
            if edge not in edges_set:
                edges_set.add(edge)
                edges.append(edge)
        
        while len(edges) < m:
            u = random.randint(1, n_left)
            v = random.randint(1, k)
            if (u, v) not in edges_set:
                edges_set.add((u, v))
                edges.append((u, v))
        edges = edges[:m]
        
        groups = defaultdict(int)
        for j in range(k):
            neighbors = []
            for u, v_edge in edges:
                if v_edge == (j + 1):
                    neighbors.append(u - 1)  # Convert to 0-based index
            key = tuple(sorted(neighbors))
            if key:
                groups[key] += c[j]
        
        sums = list(groups.values())
        expected_gcd = 0
        for s in sums:
            expected_gcd = math.gcd(expected_gcd, s)
        
        return {
            'n_left': n_left,
            'k_right': k,
            'c': c,
            'edges': edges,
            'expected_gcd': expected_gcd,
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n_left = question_case['n_left']
        k = question_case['k_right']
        m = len(question_case['edges'])
        c = question_case['c']
        edges = question_case['edges']
        
        edges_desc = '\n'.join([f"{u} {v}" for u, v in edges])
        
        prompt = f"""Wu has encountered a complex problem involving a bipartite graph and needs your help to find the solution. Here are the details:

**Problem Statement:**
Given a bipartite graph with {n_left} left vertices and {k} right vertices. Each right vertex has a value. For every non-empty subset S of left vertices, let N(S) be the right vertices adjacent to any vertex in S. f(S) is the sum of values in N(S). Find the GCD of all f(S).

**Input Format:**
- Line 1: Two integers {n_left} (left vertices) and {m} (edges).
- Line 2: {k} integers: {c}
- Next {m} lines: Two integers u v per line describing an edge:
{edges_desc}

**Output:**
- The GCD value within [ANSWER][/ANSWER], e.g., [ANSWER]5[/ANSWER]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

