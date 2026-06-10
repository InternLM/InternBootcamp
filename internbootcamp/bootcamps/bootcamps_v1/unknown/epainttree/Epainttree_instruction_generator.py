import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import functools
from collections import defaultdict

# === 源文件中的全局函数 ===

def generate_random_tree_edges(n):
    if n == 1:
        return []
    if n == 2:
        return [(1, 2)]
    prufer = [random.randint(1, n) for _ in range(n-2)]
    degree = defaultdict(int)
    for node in prufer:
        degree[node] += 1
    leaves = []
    for v in range(1, n+1):
        if degree[v] == 0:
            leaves.append(v)
    edges = []
    for node in prufer:
        leaf = leaves.pop(0)
        edges.append((leaf, node))
        degree[leaf] -= 1
        degree[node] -= 1
        if degree[node] == 0:
            leaves.append(node)
        leaves.sort()
    edges.append((leaves[0], leaves[1]))
    edges = [tuple(sorted(e)) for e in edges]
    return edges[:n-1]

def generate_points(n, min_coord=-10**9, max_coord=10**9):
    xs = random.sample(range(min_coord, max_coord + 1), n)
    ys = [x**2 + random.randint(-1000, 1000) for x in xs]
    return list(zip(xs, ys))

def generate_solution(n, edges, points):
    g = [[] for _ in range(n)]
    for u, v in edges:
        u0 = u - 1
        v0 = v - 1
        g[u0].append(v0)
        g[v0].append(u0)
    p_list = [{'x': x, 'y': y, 'id': i} for i, (x, y) in enumerate(points)]
    size = [1] * n

    def dfs(v, parent):
        total = 1
        for to in g[v]:
            if to != parent:
                total += dfs(to, v)
        size[v] = total
        return total
    dfs(0, -1)
    sorted_p = sorted(p_list, key=lambda pt: (-pt['y'], pt['x']))
    ans = [0] * n

    def rec(v, pts, parent):
        if not pts:
            return
        current = pts[0]
        ans[current['id']] = v
        remaining = pts[1:]
        if not remaining:
            return
        gx, gy = current['x'], current['y']
        def compare(a, b):
            val = (a['x'] - gx) * (b['y'] - gy) - (b['x'] - gx) * (a['y'] - gy)
            return -1 if val > 0 else 1 if val < 0 else 0
        remaining_sorted = sorted(remaining, key=functools.cmp_to_key(compare))
        cur = 0
        for to in g[v]:
            if to != parent:
                subset = remaining_sorted[cur:cur + size[to]]
                cur += size[to]
                rec(to, subset, v)
    rec(0, sorted_p, -1)
    return [ans[i] + 1 for i in range(n)]

def segments_intersect(a, b, c, d):
    def ccw(A, B, C):
        return (B[0]-A[0])*(C[1]-A[1]) - (B[1]-A[1])*(C[0]-A[0])
    ccw1 = ccw(a, b, c)
    ccw2 = ccw(a, b, d)
    ccw3 = ccw(c, d, a)
    ccw4 = ccw(c, d, b)
    
    if (ccw1 * ccw2 < 0) and (ccw3 * ccw4 < 0):
        return True
    
    def on_segment(p, a, b):
        return (min(a[0], b[0]) <= p[0] <= max(a[0], b[0])) and \
               (min(a[1], b[1]) <= p[1] <= max(a[1], b[1])) and \
               (ccw(a, b, p) == 0)
    
    return on_segment(c, a, b) or on_segment(d, a, b) or \
           on_segment(a, c, d) or on_segment(b, c, d)


class EpainttreeInstructionGenerator(BaseInstructionGenerator):
    """Epainttree Bootcamp指令生成器"""
    
    def __init__(self, n=3, min_coord=-10**9, max_coord=10**9):
        """
        初始化Epainttree指令生成器
        
        Args:
            n: 参数描述
            min_coord: 参数描述
            max_coord: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.min_coord = min_coord
        self.max_coord = max_coord
    
    def case_generator(self):
        while True:
            edges = generate_random_tree_edges(self.n)
            points = generate_points(self.n, self.min_coord, self.max_coord)
            try:
                solution = generate_solution(self.n, edges, points)
                if sorted(solution) == list(range(1, self.n+1)):
                    return {
                        'n': self.n,
                        'edges': edges,
                        'points': points
                    }
            except:
                continue
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        points = question_case['points']
        problem = f"""You are given a tree with {n} vertices and {n} points on a plane. No three points lie on the same straight line. Your task is to assign each vertex of the tree to exactly one of the given points such that when the tree is drawn on the plane with edges as line segments between corresponding points, the following conditions are met:
1. Each vertex is assigned to a distinct point.
2. For any two adjacent vertices in the tree, their corresponding points are connected by a segment.
3. No two segments corresponding to non-adjacent edges in the tree intersect each other, except at common endpoints for adjacent edges.

Input format:
- The first line contains an integer n ({n} in this case).
- The next {n-1} lines describe the edges of the tree.
- The next {n} lines give the coordinates of the points.

Output format:
Print {n} distinct integers where the i-th integer represents the vertex assigned to the i-th point (in the order the points are given). The vertices are numbered from 1 to {n}.

The input for this case is:
{n}
"""
        for u, v in edges:
            problem += f"{u} {v}\n"
        for x, y in points:
            problem += f"{x} {y}\n"
        problem += "\nProvide your answer within [answer] and [/answer] tags."
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

