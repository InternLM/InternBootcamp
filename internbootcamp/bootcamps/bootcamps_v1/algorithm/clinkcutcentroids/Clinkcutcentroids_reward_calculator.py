import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict




class ClinkcutcentroidsRewardCalculator(BaseRewardCalculator):
    """Clinkcutcentroids奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        try:
            answer_block = output.split('[answer]')[-1].split('[/answer]')[0].strip()
            lines = [line.strip() for line in answer_block.split('\n') if line.strip()]
            cut = tuple(map(int, lines[0].split()))
            add = tuple(map(int, lines[1].split()))
            return (cut, add)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # Edge case validation
        if not solution or len(solution) != 2:
            return False
        cut, add = solution
        n = identity['n']
        edges = {frozenset((u, v)) for u, v in identity['edges']}
        
        # Validate cut edge exists
        if frozenset(cut) not in edges:
            return False
        
        # Build new edge set
        new_edges = [e for e in edges if e != frozenset(cut)]
        new_edges.append(frozenset(add))
        if len(new_edges) != n-1:
            return False
        
        # Check connectivity
        adj = defaultdict(list)
        for e in new_edges:
            u, v = e
            adj[u].append(v)
            adj[v].append(u)
        
        visited = set()
        stack = [1]  # Trees are connected by definition
        while stack:
            u = stack.pop()
            if u not in visited:
                visited.add(u)
                for v in adj[u]:
                    if v not in visited:
                        stack.append(v)
        if len(visited) != n:
            return False
        
        # Centroid verification
        centroids = cls.find_centroids(n, adj)
        return len(centroids) == 1
    
    # 其他额外方法

