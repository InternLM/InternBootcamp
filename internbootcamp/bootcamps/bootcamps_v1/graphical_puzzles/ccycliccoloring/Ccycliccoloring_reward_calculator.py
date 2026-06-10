import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from math import gcd
from collections import deque




class CcycliccoloringRewardCalculator(BaseRewardCalculator):
    """Ccycliccoloring奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return int(matches[-1].strip()) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 精确验证算法
        n = identity['n']
        edges = identity['edges']
        
        # 自环特判
        if any(u == v for u, v in edges):
            return solution == 1
        
        # 构建邻接表
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u-1].append(v-1)
        
        # 计算最大k的算法实现
        visited = [False] * n
        color = [0] * n
        
        def dfs(u, c):
            color[u] = c
            visited[u] = True
            for v in adj[u]:
                if not visited[v]:
                    if not dfs(v, c + 1):
                        return False
                elif color[v] != (c + 1) % solution:
                    return False
            return True
        
        # 检查所有连通分量
        for i in range(n):
            if not visited[i]:
                if not dfs(i, 0):
                    return False
        return True
    
    # 其他额外方法

