import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CmishaandforestRewardCalculator(BaseRewardCalculator):
    """Cmishaandforest奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 增强正则表达式容错能力
        import re
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        content = matches[-1].strip()
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        if not lines:
            return None
        try:
            m = int(lines[0])
            edges = []
            for line in lines[1:m+1]:
                parts = list(map(int, line.split()))
                if len(parts) != 2:
                    return None
                a, b = parts
                edges.append((a, b))
            return edges
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 增加边界情况校验
        if solution is None or not isinstance(solution, list):
            return False
        
        n = identity['n']
        expected_degrees = identity['degrees']
        expected_s = identity['s_list']
        edges = solution
        
        # 处理空森林特殊情况
        if n == 0:
            return len(edges) == 0
        
        edge_set = set()
        for a, b in edges:
            if a < 0 or a >= n or b < 0 or b >= n:
                return False
            if a == b:
                return False
            u, v = (a, b) if a < b else (b, a)
            if (u, v) in edge_set:
                return False
            edge_set.add((u, v))
        
        # 验证边数有效性
        if 2 * len(edges) != sum(expected_degrees):
            return False
        
        # 重建邻接表并验证属性
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)
        
        # 验证度数和异或和
        for i in range(n):
            if len(adj[i]) != expected_degrees[i]:
                return False
            s = 0
            for neighbor in adj[i]:
                s ^= neighbor
            if s != expected_s[i]:
                return False
        
        # 验证森林结构（无环）
        parent = list(range(n))
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        
        for a, b in edges:
            pa, pb = find(a), find(b)
            if pa == pb:
                return False  # 存在环
            parent[pa] = pb
        
        return True
    
    # 其他额外方法

