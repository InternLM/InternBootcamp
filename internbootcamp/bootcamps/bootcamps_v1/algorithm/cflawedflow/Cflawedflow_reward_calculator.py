import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque

# === 源文件中的其他类 ===

class Edge:
    def __init__(self, from_, to_, w_, id_):
        self.from_ = from_
        self.to_ = to_
        self.w_ = w_
        self.id_ = id_


class CflawedflowRewardCalculator(BaseRewardCalculator):
    """Cflawedflow奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        digits = re.findall(r'\b[01]\b', matches[-1])
        return [int(d) for d in digits] if digits and len(digits) == len(matches[-1].split()) else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if len(solution) != identity["m"]:
            return False
        
        edges = identity["edges"]
        n = identity["n"]
        
        # Check source has no incoming edges
        for (a, b, _), d in zip(edges, solution):
            if (d == 0 and b == 1) or (d == 1 and a == 1):
                return False
        
        # Flow conservation check
        inflow = defaultdict(int)
        outflow = defaultdict(int)
        for (a, b, c), d in zip(edges, solution):
            if d == 0:
                outflow[a] += c
                inflow[b] += c
            else:
                outflow[b] += c
                inflow[a] += c
        
        for v in range(2, n):
            if inflow.get(v, 0) != outflow.get(v, 0):
                return False
        
        # Acyclicity check with topological sort
        adj = [[] for _ in range(n+1)]
        in_degree = [0]*(n+1)
        for (a, b, _), d in zip(edges, solution):
            u, v = (a, b) if d == 0 else (b, a)
            adj[u].append(v)
            in_degree[v] += 1
        
        q = deque([u for u in range(1, n+1) if in_degree[u] == 0])
        visited = 0
        while q:
            u = q.popleft()
            visited += 1
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    q.append(v)
        
        return visited == n  # All nodes must be visited for acyclic graph
    
    # 其他额外方法

