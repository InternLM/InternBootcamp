import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class ExenonsattackonthegangsRewardCalculator(BaseRewardCalculator):
    """Exenonsattackonthegangs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        edges = identity['edges']
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
        
        sub = {}
        fa = {}
        for root in range(1, n+1):
            sub[root] = {}
            fa[root] = {}
            stack = [(root, -1)]  # (node, parent)
            sub[root][root] = 1
            fa[root][root] = -1  # Mark root's parent as -1
            while stack:
                node, parent = stack.pop()
                for neighbor in adj[node]:
                    if neighbor != parent:
                        fa[root][neighbor] = node
                        stack.append((neighbor, node))
            # Calculate subtree sizes using BFS from leaves
            post_order = []
            stack = [(root, -1, False)]
            while stack:
                node, parent, visited = stack.pop()
                if visited:
                    post_order.append(node)
                    total = 1
                    for neighbor in adj[node]:
                        if neighbor != parent and fa[root].get(neighbor, -1) == node:
                            total += sub[root][neighbor]
                    sub[root][node] = total
                else:
                    stack.append((node, parent, True))
                    for neighbor in adj[node]:
                        if neighbor != parent:
                            stack.append((neighbor, node, False))
        
        memo = {}
        pairs = [(i, j) for i in range(1, n+1) for j in range(1, n+1) if i != j]
        stack = pairs.copy()
        processed = set()
        
        while stack:
            a, b = stack.pop()
            if (a, b) in processed:
                continue
            if a == b:
                memo[(a, b)] = 0
                processed.add((a, b))
                continue
            
            fa_a_b = fa[a].get(b, -1)
            fa_b_a = fa[b].get(a, -1)
            deps = []
            if fa_a_b != -1 and (fa_a_b, a) not in memo:
                deps.append((fa_a_b, a))
            if fa_b_a != -1 and (fa_b_a, b) not in memo:
                deps.append((fa_b_a, b))
            
            if deps:
                stack.append((a, b))
                stack.extend(deps)
                continue
            
            opt1 = memo.get((fa_a_b, a), 0) if fa_a_b != -1 else 0
            opt2 = memo.get((fa_b_a, b), 0) if fa_b_a != -1 else 0
            memo[(a, b)] = sub[a][b] * sub[b][a] + max(opt1, opt2)
            processed.add((a, b))
        
        max_s = max(memo.values()) if memo else 0
        return solution == max_s
    
    # 其他额外方法

