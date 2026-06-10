import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CannasvyatoslavandmapsRewardCalculator(BaseRewardCalculator):
    """Cannasvyatoslavandmaps奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        match = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not match:
            return None
        last_answer = match[-1].strip()
        numbers = list(map(int, re.findall(r'\d+', last_answer)))
        if len(numbers) < 2:
            return None
        return numbers[1:]
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # Validate basic format
        if len(solution) < 2 or solution[0] != identity['p'][0] or solution[-1] != identity['p'][-1]:
            return False
        
        # Check subsequence condition
        p_iter = iter(identity['p'])
        try:
            for v in solution:
                while next(p_iter) != v:
                    pass
        except StopIteration:
            return False

        # Validate path is shortest
        n = identity['n']
        adj = [[int(c) for c in row] for row in identity['adj_matrix']]
        
        # Build distance matrix
        dist = [[float('inf')]*n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
            for j in range(n):
                if adj[i][j]:
                    dist[i][j] = 1
        
        # Floyd-Warshall
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])
        
        # Calculate required path length
        total = 0
        for i in range(len(solution)-1):
            u = solution[i]-1
            v = solution[i+1]-1
            if dist[u][v] == float('inf'):
                return False
            total += dist[u][v]
        
        return total == (identity['m'] - 1)
    
    # 其他额外方法

