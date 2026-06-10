import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class EpainttreeRewardCalculator(BaseRewardCalculator):
    """Epainttree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last = matches[-1].strip()
        try:
            return list(map(int, last.split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        edges = identity['edges']
        points = identity['points']
        if solution is None or len(solution) != n or sorted(solution) != list(range(1, n+1)):
            return False
        
        vertex_to_point = {solution[i]: points[i] for i in range(n)}
        segments = []
        adj_edges = defaultdict(set)
        for u, v in edges:
            adj_edges[u].add(v)
            adj_edges[v].add(u)
            p1 = vertex_to_point[u]
            p2 = vertex_to_point[v]
            segments.append((p1, p2))
        
        for i in range(len(segments)):
            a, b = segments[i]
            u1, v1 = edges[i]
            for j in range(i+1, len(segments)):
                c, d = segments[j]
                u2, v2 = edges[j]
                if u2 in adj_edges[u1] or u2 in adj_edges[v1] or v2 in adj_edges[u1] or v2 in adj_edges[v1]:
                    continue
                if segments_intersect(a, b, c, d):
                    return False
        return True
    
    # 其他额外方法

