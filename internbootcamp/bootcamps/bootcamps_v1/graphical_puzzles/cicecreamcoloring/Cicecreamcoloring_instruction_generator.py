import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import deque




class CicecreamcoloringInstructionGenerator(BaseInstructionGenerator):
    """Cicecreamcoloring Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cicecreamcoloring指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.default_params = {
            'n_range': (3, 5),
            'm_range': (2, 5),
            'max_type_nodes': 3,
            'prob_assign': 0.8
        }
        self.params = self.default_params.copy()
        self.params.update(params)
    
    def case_generator(self):
        params = self.params
        n = random.randint(*params['n_range'])
        m = random.randint(*params['m_range'])
        edges = self.generate_random_tree(n)
        
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        nodes = [[] for _ in range(n+1)]
        
        for ice_type in range(1, m+1):
            if random.random() > params['prob_assign']:
                continue
                
            max_size = random.randint(1, params['max_type_nodes'])
            start_node = random.randint(1, n)
            connected_nodes = self.bfs_connected_subset(adj, start_node, max_size)
            
            for node in connected_nodes:
                nodes[node].append(ice_type)
        
        nodes_data = []
        for i in range(1, n+1):
            types = sorted(nodes[i])
            nodes_data.append({'types': types})
        
        total_si = sum(len(nd['types']) for nd in nodes_data)
        if total_si > 5*10**5:
            return self.case_generator()
        
        return {
            'n': n,
            'm': m,
            'nodes': nodes_data,
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        nodes = question_case['nodes']
        edges = question_case['edges']
        
        input_lines = [f"{n} {m}"]
        for node in nodes:
            si = len(node['types'])
            if si == 0:
                input_lines.append("0")
            else:
                input_lines.append(f"{si} {' '.join(map(str, node['types']))}")
        for u, v in edges:
            input_lines.append(f"{u} {v}")
        
        # 显式生成input_str避免转义问题
        input_str = '\n'.join(input_lines)
        
        return f"""请解决以下冰淇淋着色问题：

输入：
{input_str}

输出要求：
1. 第一行输出最小颜色数c
2. 第二行输出m个颜色值（空格分隔）
答案请按如下格式包裹在[answer]标签内：
[answer]
c值
颜色列表
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_random_tree(self, n):
        if n == 1:
            return []
        parents = [0] * n
        for i in range(1, n):
            parents[i] = random.randint(0, i-1)
        return [(i+1, parents[i]+1) for i in range(1, n)]

    def bfs_connected_subset(self, adj, start, max_size):
        visited = set([start])
        q = deque([start])
        while q and len(visited) < max_size:
            u = q.popleft()
            for v in adj[u]:
                if v not in visited:
                    visited.add(v)
                    q.append(v)
                    if len(visited) == max_size:
                        break
        return list(visited)
