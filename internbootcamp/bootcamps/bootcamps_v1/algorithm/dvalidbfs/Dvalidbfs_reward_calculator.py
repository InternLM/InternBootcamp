import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque




class DvalidbfsRewardCalculator(BaseRewardCalculator):
    """Dvalidbfs奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        start = output.rfind('[answer]')
        if start == -1:
            return None
        end = output.find('[/answer]', start)
        if end == -1:
            return None
        answer = output[start+8:end].strip().lower()
        return answer if answer in ('yes', 'no') else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        edges = identity['edges']
        given_sequence = identity['sequence']
        
        if given_sequence[0] != 1:
            return solution == 'no'
        
        mapp = [-1] * (n + 1)
        for i, node in enumerate(given_sequence):
            mapp[node] = i
        
        adj = [[] for _ in range(n + 1)]
        for u, v in edges:
            a = mapp[u]
            b = mapp[v]
            adj[a].append((b, v))
            adj[b].append((a, u))
        
        for i in range(n + 1):
            adj[i].sort(key=lambda x: x[0])
        
        new_adj = [[] for _ in range(n + 1)]
        for i in range(n + 1):
            for (level, node) in adj[i]:
                new_adj[i].append(node)
        
        visited = [False] * (n + 1)
        q = deque([1])
        visited[1] = True
        bfs_order = []
        while q:
            v = q.popleft()
            bfs_order.append(v)
            for u in new_adj[v]:
                if not visited[u]:
                    visited[u] = True
                    q.append(u)
        
        is_valid = (bfs_order == given_sequence)
        
        return (solution == 'yes' and is_valid) or (solution == 'no' and not is_valid)
    
    # 其他额外方法

