import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class DnudistbeachRewardCalculator(BaseRewardCalculator):
    """Dnudistbeach奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        content = matches[-1].strip()
        try:
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            r = int(lines[0])
            cities = list(map(int, lines[1].split()))
            if r != len(cities) or r < 1:
                return None
            if len(set(cities)) != len(cities):
                return None
            return {'r': r, 'cities': cities}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        
        cities = solution['cities']
        r = solution['r']
        
        # 基础校验
        if r != len(cities) or r < 1:
            return False
        if any(c in identity['fortresses'] for c in cities):
            return False
        if any(c < 1 or c > identity['n'] for c in cities):
            return False
        if len(set(cities)) != len(cities):
            return False
        
        # 构建邻接表
        adj = {c: set() for c in range(1, identity['n']+1)}
        for a, b in identity['roads']:
            adj[a].add(b)
            adj[b].add(a)
        
        # 计算实际最小强度值
        current_min = float('inf')
        for city in cities:
            neighbors = adj[city]
            in_solution = sum(1 for n in neighbors if n in cities)
            strength = in_solution / len(neighbors)
            current_min = min(current_min, strength)
        
        # 允许浮点误差
        return abs(current_min - identity['max_min_strength']) < 1e-6
    
    # 其他额外方法

