import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class F1fallingsandeasyversionRewardCalculator(BaseRewardCalculator):
    """F1fallingsandeasyversion奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # Use a more robust regular expression to extract the answer
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        return int(matches[-1])
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        grid = identity['grid']
        a = identity['a']
        n = len(grid)
        m = len(grid[0]) if n > 0 else 0
        
        sand_blocks = []
        for i in range(n):
            for j in range(m):
                if grid[i][j] == '#':
                    sand_blocks.append((i, j))
        
        if not sand_blocks:
            return solution == 0
        
        idx_map = {(i, j): idx for idx, (i, j) in enumerate(sand_blocks)}
        total = len(sand_blocks)
        graph = defaultdict(list)
        reverse_graph = defaultdict(list)
        
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for idx, (i, j) in enumerate(sand_blocks):
            for di, dj in directions:
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < m and grid[ni][nj] == '#':
                    if (ni, nj) in idx_map:
                        neighbor_idx = idx_map[(ni, nj)]
                        if neighbor_idx != idx:
                            graph[idx].append(neighbor_idx)
                            reverse_graph[neighbor_idx].append(idx)
        
        visited = [False] * total
        order = []
        
        def dfs(u):
            stack = [(u, False)]
            while stack:
                node, processed = stack.pop()
                if processed:
                    order.append(node)
                    continue
                if visited[node]:
                    continue
                visited[node] = True
                stack.append((node, True))
                for v in graph[node]:
                    if not visited[v]:
                        stack.append((v, False))
        
        for i in range(total):
            if not visited[i]:
                dfs(i)
        
        visited = [False] * total
        component = [0] * total
        current_component = 0
        
        def reverse_dfs(u, label):
            stack = [u]
            visited[u] = True
            component[u] = label
            while stack:
                node = stack.pop()
                for v in reverse_graph[node]:
                    if not visited[v]:
                        visited[v] = True
                        component[v] = label
                        stack.append(v)
        
        for node in reversed(order):
            if not visited[node]:
                reverse_dfs(node, current_component)
                current_component += 1
        
        in_degree = defaultdict(int)
        for u in range(total):
            for v in graph[u]:
                if component[u] != component[v]:
                    in_degree[component[v]] += 1
        
        count = 0
        for i in range(current_component):
            if in_degree[i] == 0:
                count += 1
        
        return solution == count
    
    # 其他额外方法

