import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque

# === 源文件中的全局函数 ===

def generate_tree_edges(n):
    if n == 1:
        return []
    parents = [0] * (n + 1)  # 1-based index
    for i in range(2, n + 1):
        parents[i] = random.randint(1, i - 1)
    return [(parents[i], i) for i in range(2, n + 1)]

def generate_p(n, m):
    if m == 0:
        return [0] * n
    p = []
    remaining = m
    for _ in range(n - 1):
        val = random.randint(0, remaining)
        p.append(val)
        remaining -= val
    p.append(remaining)
    return p

def build_tree_and_parents(n, edges):
    adj = [[] for _ in range(n + 1)]  # 1-based
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    parent = [0] * (n + 1)
    visited = [False] * (n + 1)
    q = deque([1])
    visited[1] = True
    while q:
        u = q.popleft()
        for v in adj[u]:
            if not visited[v]:
                visited[v] = True
                parent[v] = u
                q.append(v)
    return parent

def dfs(graph, p, h, start=0):
    n = len(graph)
    dp = [[0, 0] for _ in range(n)]
    visited, finished = [False]*n, [False]*n
    stack = [start]
    while stack:
        curr = stack[-1]
        if not visited[curr]:
            visited[curr] = True
            for child in graph[curr]:
                if not visited[child]:
                    stack.append(child)
        else:
            curr = stack.pop()
            dp[curr][0] = p[curr]
            dp[curr][1] = 0
            for child in graph[curr]:
                if finished[child]:
                    dp[curr][0] += dp[child][0]
                    dp[curr][1] += dp[child][1]
            lower = dp[curr][1] - dp[curr][0]
            upper = dp[curr][1] + dp[curr][0]
            if not (lower <= h[curr] <= upper and (h[curr] - lower) % 2 == 0):
                return False
            v = (h[curr] - lower) // 2
            dp[curr][1] += v
            dp[curr][0] -= v
            finished[curr] = True
    return True

def main():
    t = int(input())
    for _ in range(t):
        n, m = map(int, input().split())
        p = list(map(int, input().split()))
        h = list(map(int, input().split()))
        graph = [[] for _ in range(n)]
        for _ in range(n-1):
            x, y = map(int, input().split())
            x -= 1; y -= 1
            graph[x].append(y); graph[y].append(x)
        tree = [[] for _ in range(n)]
        visited = [False]*n
        stack = [0]
        while stack:
            curr = stack.pop()
            visited[curr] = True
            for child in graph[curr]:
                if not visited[child]:
                    tree[curr].append(child)
                    stack.append(child)
        print("YES" if dfs(tree, p, h) else "NO")


class CunclebogdanandcountryhappinessRewardCalculator(BaseRewardCalculator):
    """Cunclebogdanandcountryhappiness奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().upper()
        return answer if answer in {'YES', 'NO'} else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected_answer']
    
    # 其他额外方法

