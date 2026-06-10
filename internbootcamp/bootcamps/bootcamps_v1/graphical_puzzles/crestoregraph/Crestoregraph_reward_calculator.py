import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict
from math import ceil




class CrestoregraphRewardCalculator(BaseRewardCalculator):
    """Crestoregraph奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip()
        lines = [line.strip() for line in answer.split('\n') if line.strip()]
        if not lines:
            return None
        if lines[0] == '-1':
            return '-1'
        try:
            m = int(lines[0])
            edges = []
            for line in lines[1:m+1]:
                parts = line.split()
                if len(parts) != 2:
                    continue
                a, b = map(int, parts)
                if a == b:
                    continue
                a, b = sorted((a, b))
                edges.append((a, b))
            edges = list(set(edges))
            edges.sort()
            return {'m': len(edges), 'edges': edges}
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        def reference_solve(n, k, d_list):
            v = d_list
            s = [0] * n
            for x in v:
                if x >= n or x < 0:
                    return (-1, [])
                s[x] += 1

            if s[0] != 1:
                return (-1, [])
            
            max_d = max(v)
            for i in range(max_d + 1):
                if s[i] == 0:
                    return (-1, [])
            
            for i in range(max_d):
                allowed = s[i] * (k - (i != 0))
                if s[i+1] > allowed:
                    return (-1, [])
            
            idx = [[] for _ in range(n)]
            for node, dist in enumerate(v, 1):
                idx[dist].append(node)
            
            edges = []
            try:
                for dist in range(1, max_d + 1):
                    parents = idx[dist-1]
                    children = idx[dist]
                    if not parents or not children:
                        return (-1, [])
                    
                    slots_per_parent = k - (1 if dist-1 !=0 else 0)
                    required_parents = ceil(len(children) / slots_per_parent)
                    if len(parents) < required_parents:
                        return (-1, [])
                    
                    for i, child in enumerate(children):
                        parent_idx = i // slots_per_parent
                        if parent_idx >= len(parents):
                            return (-1, [])
                        edges.append((parents[parent_idx], child))
            except:
                return (-1, [])
            
            unique_edges = set()
            degrees = defaultdict(int)
            for a, b in edges:
                if a == b:
                    continue
                a, b = sorted((a, b))
                unique_edges.add((a, b))
                degrees[a] += 1
                degrees[b] += 1
                if degrees[a] > k or degrees[b] > k:
                    return (-1, [])
            
            return (len(unique_edges), sorted(unique_edges))

        n = identity['n']
        k = identity['k']
        d_list = identity['d']
        ref_m, ref_edges = reference_solve(n, k, d_list)
        
        if solution == '-1':
            return ref_m == -1
        
        if isinstance(solution, dict):
            user_m = solution.get('m', 0)
            user_edges = set(tuple(e) for e in solution.get('edges', []))
            if ref_m == -1:
                return False
            
            # Check edge count and content
            if user_m != ref_m or user_edges != set(ref_edges):
                return False
            
            # Check degree constraints
            degrees = defaultdict(int)
            for a, b in user_edges:
                degrees[a] += 1
                degrees[b] += 1
                if degrees[a] > k or degrees[b] > k:
                    return False
            
            # Check connectivity and distances
            try:
                adj = defaultdict(list)
                for a, b in user_edges:
                    adj[a].append(b)
                    adj[b].append(a)
                
                source = d_list.index(0) + 1
                visited = {source: 0}
                queue = [source]
                for node in queue:
                    for neighbor in adj[node]:
                        if neighbor not in visited:
                            visited[neighbor] = visited[node] + 1
                            queue.append(neighbor)
                
                for i, d_val in enumerate(d_list):
                    node = i + 1
                    if visited.get(node, -1) != d_val:
                        return False
            except:
                return False
            
            return True
        
        return False
    
    # 其他额外方法

