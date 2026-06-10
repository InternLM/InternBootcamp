import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque

# === 源文件中的全局函数 ===

def generate_valid_graph(n, m):
    """生成每个节点度数至少为1的图（不要求连通）"""
    if n < 2:
        raise ValueError("n must be at least 2")
    if m < n//2:
        m = max(m, n//2)  # 保证足够的最小边数
    
    edges = set()
    nodes = list(range(1, n+1))
    random.shuffle(nodes)
    
    # 保证每个节点至少有一个边
    remaining = nodes.copy()
    while remaining:
        if len(remaining) == 1:
            # 最后一个节点随机连接到已有节点
            node = remaining.pop()
            candidates = [x for x in nodes if x != node]
            if not candidates:
                raise ValueError("Can't create valid graph")
            neighbor = random.choice(candidates)
            edge = tuple(sorted((node, neighbor)))
            edges.add(edge)
        else:
            a = remaining.pop()
            b = remaining.pop()
            edge = tuple(sorted((a, b)))
            edges.add(edge)
    
    # 添加剩余边
    possible_edges = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1) if (i, j) not in edges]
    while len(edges) < m and possible_edges:
        edge = possible_edges.pop(random.randint(0, len(possible_edges)-1))
        edges.add(edge)
    
    return sorted(edges)[:m]

def solve_case(n, m, k, fortresses, roads):
    bad = {f-1 for f in fortresses}
    adj = [[] for _ in range(n)]
    
    for a, b in roads:
        a0, b0 = a-1, b-1
        adj[a0].append(b0)
        adj[b0].append(a0)
    
    total_degree = [len(neighbors) for neighbors in adj]
    good_degree = [len(neighbors) for neighbors in adj]
    
    for u in bad:
        for v in adj[u]:
            good_degree[v] -= 1
    
    low, high = 0.0, 1.0
    best_solution = []
    
    for _ in range(50):
        mid = (low + high) / 2
        removed = set()
        current_good = good_degree.copy()
        queue = deque()
        
        for city in range(n):
            if city not in bad and total_degree[city] > 0:
                ratio = current_good[city] / total_degree[city]
                if ratio <= mid - 1e-9:
                    queue.append(city)
                    removed.add(city)
        
        temp_removed = set(removed)
        while queue:
            u = queue.popleft()
            for v in adj[u]:
                if v not in bad and v not in temp_removed:
                    current_good[v] -= 1
                    if current_good[v]/total_degree[v] <= mid - 1e-9:
                        queue.append(v)
                        temp_removed.add(v)
        
        valid_cities = [city for city in range(n) if city not in bad and city not in temp_removed]
        if valid_cities:
            low = mid
            best_solution = [c+1 for c in valid_cities]
        else:
            high = mid
    
    return best_solution


class DnudistbeachInstructionGenerator(BaseInstructionGenerator):
    """Dnudistbeach Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dnudistbeach指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        default_params = {'n': 8, 'm': 10, 'k': 2}
        default_params.update(params)

        # 参数校验
        n = max(2, default_params['n'])
        m = max(n-1, default_params['m'])  # 确保足够的最小边数
        k = max(1, min(default_params['k'], n-1))

        self.params = {'n': n, 'm': m, 'k': k}
        self.n = n
        self.m = m
        self.k = k
    
    def case_generator(self):
        n, m, k = self.n, self.m, self.k
        fortresses = random.sample(range(1, n+1), k)
        
        # 生成保证每个城市有至少一条路的图
        roads = generate_valid_graph(n, m)
        
        # 计算正确答案
        correct_solution = solve_case(n, m, k, fortresses, roads)
        
        # 验证解决方案存在
        if not correct_solution:
            raise RuntimeError("Failed to generate valid solution")
        
        # 计算最小强度值
        adj = {city: set() for city in range(1, n+1)}
        for a, b in roads:
            adj[a].add(b)
            adj[b].add(a)
        
        min_strength = min(
            sum(1 for neighbor in adj[city] if neighbor in correct_solution) / len(adj[city])
            for city in correct_solution
        )
        
        return {
            'n': n, 'm': m, 'k': k,
            'fortresses': sorted(fortresses),
            'roads': roads,
            'correct_answer': correct_solution,
            'max_min_strength': min_strength
        }
    
    @staticmethod
    def prompt_func(question_case):
        fortress_list = ', '.join(map(str, question_case['fortresses']))
        road_list = '\n'.join(f'{a} {b}' for a, b in question_case['roads'])
        return f"""Nudist Beach军事行动需要选择占领城市集合。已知：
- 总城市数：{question_case['n']}个（编号1~{question_case['n']}）
- 道路数量：{question_case['m']}条
- 禁城列表：{fortress_list}

规则：
1. 必须选择非空的非禁城集合
2. 每个被占城市的强度 = (被占邻居数)/(总邻居数)
3. 目标：最大化集合中最小的强度值

道路连接：
{road_list}

请给出最优解。答案格式：
[answer]
第一行：城市数量r
第二行：用空格分隔的r个城市编号
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

