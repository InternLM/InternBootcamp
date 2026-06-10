import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import heapq
import random
import re

# === 源文件中的全局函数 ===

def compute_min_lex_sequence(n, edges):
    adj = [[] for _ in range(n)]
    for u, v in edges:
        u_zero = u - 1
        v_zero = v - 1
        adj[u_zero].append(v_zero)
        adj[v_zero].append(u_zero)
    
    heap = []
    heapq.heappush(heap, 0)
    visited = [False] * n
    result = []
    
    while heap:
        current = heapq.heappop(heap)
        if visited[current]:
            continue
        visited[current] = True
        result.append(current + 1)
        for neighbor in sorted(adj[current]):  # 需要排序保证稳定性
            if not visited[neighbor]:
                heapq.heappush(heap, neighbor)
    return result


class DlunarnewyearandawanderRewardCalculator(BaseRewardCalculator):
    """Dlunarnewyearandawander奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        return list(map(int, re.findall(r'\d+', matches[-1]))) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

