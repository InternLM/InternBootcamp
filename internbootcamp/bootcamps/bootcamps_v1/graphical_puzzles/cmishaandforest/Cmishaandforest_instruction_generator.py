import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CmishaandforestInstructionGenerator(BaseInstructionGenerator):
    """Cmishaandforest Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cmishaandforest指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 修正点1：扩大默认参数范围以支持更小的n值
        self.min_n = params.get('min_n', 1)
        self.max_n = params.get('max_n', 10)
        self.n = params.get('n', None)
    
    def case_generator(self):
        if self.n is not None:
            n = self.n
        else:
            n = random.randint(self.min_n, self.max_n)
        
        parent = list(range(n))
        edges = []
        possible_edges = [(u, v) for u in range(n) for v in range(u+1, n)]
        random.shuffle(possible_edges)
        
        # 修正点2：保证m的取值范围覆盖所有合法情况
        max_m = n - 1 if n > 0 else 0
        m = random.randint(0, max_m)
        
        for u, v in possible_edges:
            if len(edges) == m:
                break
            # 使用路径压缩优化并查集
            pu, pv = u, v
            while parent[pu] != pu:
                parent[pu] = parent[parent[pu]]
                pu = parent[pu]
            while parent[pv] != pv:
                parent[pv] = parent[parent[pv]]
                pv = parent[pv]
            if pu != pv:
                parent[pu] = pv
                edges.append((u, v))
        
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        degrees = [len(neighbors) for neighbors in adj]
        s_list = []
        for i in range(n):
            s = 0
            for neighbor in adj[i]:
                s ^= neighbor
            s_list.append(s)
        
        return {
            'n': n,
            'degrees': degrees,
            's_list': s_list
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        # 保持原有实现不变，格式更规范
        n = question_case['n']
        degrees = question_case['degrees']
        s_list = question_case['s_list']
        
        input_lines = [str(n)]
        for i in range(n):
            input_lines.append(f"{degrees[i]} {s_list[i]}")
        input_str = '\n'.join(input_lines)
        
        prompt = f"""You are a programming assistant. Help Misha reconstruct the original forest based on the degree and XOR sum values of each vertex. The forest is a non-directed acyclic graph (no loops or parallel edges) composed of trees. Each vertex's degree is the number of adjacent vertices, and the XOR sum is the result of XORing the indices of all adjacent vertices.

Input Format:
The first line contains an integer n (1 ≤ n ≤ 2^16), the number of vertices. The next n lines each contain two integers: degree_i and s_i (the degree and XOR sum of vertex i, 0-based).

Output Format:
The first line should be the number of edges m. The following m lines each contain two distinct integers a and b, representing an edge between vertices a and b. The order of edges and the order of vertices in each edge do not matter.

Example Input:
3
2 3
1 0
1 0

Example Output:
2
0 1
0 2

Your task is to solve the following input case. Ensure your answer is enclosed within [answer] and [/answer] tags. Here's the input:

{input_str}"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

