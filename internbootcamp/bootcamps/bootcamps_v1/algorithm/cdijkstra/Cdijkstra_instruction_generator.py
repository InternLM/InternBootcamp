import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
import heapq
import random
import re




class CdijkstraInstructionGenerator(BaseInstructionGenerator):
    """Cdijkstra Bootcamp指令生成器"""
    
    def __init__(self, n_min=5, n_max=15, edge_density=0.3, max_weight=100, ensure_path=True):
        """
        初始化Cdijkstra指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            edge_density: 参数描述
            max_weight: 参数描述
            ensure_path: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()  # 初始化基类
        self.n_min = n_min
        self.n_max = n_max
        self.edge_density = edge_density
        self.max_weight = max_weight
        self.ensure_path = ensure_path
    
    def case_generator(self):
        # 生成节点数时至少包含2个节点
        n = max(2, random.randint(self.n_min, self.n_max))
        max_possible_edges = n * (n - 1) // 2
        m = int(max_possible_edges * self.edge_density)
        
        # 生成基础边集
        edges = []
        node_list = list(range(1, n+1))
        random.shuffle(node_list)
        
        # 生成保证连通性的最小边集
        for i in range(1, len(node_list)):
            a, b = node_list[i-1], node_list[i]
            w = random.randint(1, self.max_weight)
            edges.append((a, b, w))
        
        # 添加随机边
        existing_edges = set()
        for _ in range(m - (n-1)):
            while True:
                a = random.choice(node_list)
                b = random.choice(node_list)
                if a != b and (a, b) not in existing_edges:
                    existing_edges.add((a, b))
                    existing_edges.add((b, a))
                    break
            w = random.randint(1, self.max_weight)
            edges.append((a, b, w))
        
        # 构建邻接表
        adj = defaultdict(list)
        for a, b, w in edges:
            adj[a].append((b, w))
            adj[b].append((a, w))
        
        # Dijkstra算法实现
        dist = {i: float('inf') for i in node_list}
        prev = {i: None for i in node_list}
        dist[1] = 0
        heap = [(0, 1)]
        
        while heap:
            current_dist, u = heapq.heappop(heap)
            if current_dist > dist[u]:
                continue
            for v, w in adj[u]:
                if dist[v] > current_dist + w:
                    dist[v] = current_dist + w
                    prev[v] = u
                    heapq.heappush(heap, (dist[v], v))
        
        # 处理无路径情况
        has_path = dist[n] != float('inf')
        if self.ensure_path and not has_path:
            # 添加直达路径确保连通
            w = random.randint(1, self.max_weight)
            edges.append((1, n, w))
            adj[1].append((n, w))
            adj[n].append((1, w))
            dist[n] = w
            has_path = True
        
        # 转换为可序列化格式
        return {
            'n': n,
            'edges': edges,
            'expected_distance': float(dist[n]) if has_path else -1,
            'has_path': has_path
        }
    
    @staticmethod
    def prompt_func(case):
        input_lines = [f"{case['n']} {len(case['edges'])}"]
        input_lines += [f"{a} {b} {w}" for a, b, w in case['edges']]
        
        return f"""Solve the shortest path problem in an undirected weighted graph. Find the minimal path from node 1 to node {case['n']}.

Input Format:
First line: n m (number of nodes, edges)
Next m lines: a b w (edges with weights)

Output Format:
- If path exists: space-separated node sequence
- If no path: -1

Example:
Input:
5 6
1 2 2
2 5 5
2 3 4
1 4 1
4 3 3
3 5 1

Output:
[answer]1 4 3 5[/answer]

Your Task:
{" ".join(input_lines)}
Put your final answer within [answer] tags like: [answer]your path here[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

