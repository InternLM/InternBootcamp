import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CnetworksafetyRewardCalculator(BaseRewardCalculator):
    """Cnetworksafety奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answers = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return answers[-1].strip() if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            user_ans = int(solution.strip()) % MOD
        except:
            return False

        # Reference algorithm implementation
        n, m, k = identity['n'], identity['m'], identity['k']
        c = identity['c']
        edges = [(u-1, v-1) for u, v in identity['edges']]  # Convert to 0-based
        
        d_map = defaultdict(list)
        for u, v in edges:
            d = c[u] ^ c[v]
            d_map[d].append((u, v))
        
        result = 0
        # Process each xor value
        for d, edges in d_map.items():
            adj = [[] for _ in range(n)]
            nodes = set()
            for u, v in edges:
                adj[u].append(v)
                adj[v].append(u)
                nodes.add(u)
                nodes.add(v)
            
            visited = [False] * n
            components = 0
            for node in nodes:
                if not visited[node]:
                    components += 1
                    stack = [node]
                    visited[node] = True
                    while stack:
                        u = stack.pop()
                        for v in adj[u]:
                            if not visited[v]:
                                visited[v] = True
                                stack.append(v)
            
            free_nodes = n - len(nodes)
            result = (result + pow(2, free_nodes + components, MOD)) % MOD
        
        # Handle x values not in d_map
        other_x = (pow(2, k, MOD) - len(d_map)) % MOD
        result = (result + other_x * pow(2, n, MOD)) % MOD
        
        return user_ans == result % MOD
    
    # 其他额外方法

