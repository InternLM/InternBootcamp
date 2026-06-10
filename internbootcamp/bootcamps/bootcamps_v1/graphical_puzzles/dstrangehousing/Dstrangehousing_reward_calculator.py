import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import deque




class DstrangehousingRewardCalculator(BaseRewardCalculator):
    """Dstrangehousing奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个合法答案块
        answer_blocks = []
        start = -1
        for i in range(len(output)):
            if output.startswith('[answer]', i):
                start = i + 8
            elif output.startswith('[/answer]', i) and start != -1:
                answer_blocks.append(output[start:i].strip())
                start = -1
        
        if not answer_blocks:
            return None
            
        last_answer = answer_blocks[-1].split('\n')
        cleaned = [line.strip() for line in last_answer if line.strip()]
        
        if not cleaned:
            return None
            
        if cleaned[0].upper() == 'NO':
            return 'NO'
            
        if len(cleaned) >=2 and cleaned[0].upper() == 'YES':
            try:
                k = int(cleaned[1])
                if len(cleaned) == 2 + k:
                    nums = list(map(int, cleaned[2:]))
                    return f"YES {k} {' '.join(map(str, nums))}"
            except:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 处理无效解
        if not solution:
            return False
            
        if solution == 'NO':
            return not cls._is_bipartite(identity['edges'], identity['n'])
        
        # 解析答案
        parts = solution.split()
        if len(parts) < 3 or parts[0] != 'YES':
            return False
            
        try:
            k = int(parts[1])
            S = set(map(int, parts[2:2+k]))
        except:
            return False
        
        # 条件1：独立集验证
        adj = {u: set() for u in range(1, identity['n']+1)}
        for u, v in identity['edges']:
            adj[u].add(v)
            adj[v].add(u)
            if u in S and v in S:
                return False
        
        # 条件2：开放通道后的连通性验证
        open_edges = set()
        T = set(range(1, identity['n']+1)) - S
        for u, v in identity['edges']:
            if u in S or v in S:
                open_edges.add((u, v))
        
        # 构建邻接表
        graph = {u: [] for u in range(1, identity['n']+1)}
        for u, v in open_edges:
            graph[u].append(v)
            graph[v].append(u)
        
        # BFS检查连通性
        visited = set()
        start_node = next((u for u in T if u in graph and graph[u]), None) or next(iter(S), None)
        if not start_node:
            return False
            
        queue = deque([start_node])
        visited.add(start_node)
        while queue:
            u = queue.popleft()
            for v in graph[u]:
                if v not in visited:
                    visited.add(v)
                    queue.append(v)
        
        return len(visited) == identity['n']
    
    # 其他额外方法

