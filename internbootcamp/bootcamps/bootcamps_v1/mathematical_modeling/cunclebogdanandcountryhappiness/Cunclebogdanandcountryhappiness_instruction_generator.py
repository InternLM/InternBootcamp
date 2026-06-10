import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class CunclebogdanandcountryhappinessInstructionGenerator(BaseInstructionGenerator):
    """Cunclebogdanandcountryhappiness Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=5, m_min=1, m_max=100):
        """
        初始化Cunclebogdanandcountryhappiness指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        edges = generate_tree_edges(n)
        parent = build_tree_and_parents(n, edges)
        
        # Generate p with sum m
        p = generate_p(n, m)
        
        # Generate valid h by simulating people's mood changes
        good = [0] * (n + 1)  # 1-based
        bad = [0] * (n + 1)
        
        # For each city, distribute people
        for city in range(1, n + 1):
            num_people = p[city - 1]
            if num_people == 0:
                continue
            
            # Path from capital (1) to current city
            path = []
            current = city
            while current != 1:
                path.append(current)
                current = parent[current]
            path.append(1)
            path = path[::-1]  # reverse to get path from 1 to city
            
            for _ in range(num_people):
                # Randomly choose when the mood is ruined (None means never)
                ruin_step = random.randint(0, len(path)-1)
                
                # Update mood for each city in path
                for step in range(len(path)):
                    current_city = path[step]
                    if step < ruin_step:
                        good[current_city] += 1
                    else:
                        bad[current_city] += 1
        
        # Compute h_i = good[i] - bad[i]
        h = [good[i] - bad[i] for i in range(1, n + 1)]
        
        # Randomly decide to make invalid case with 50% chance
        if random.random() < 0.5:
            # Modify h to create invalid case
            idx = random.randint(0, n-1)
            h[idx] += random.choice([-1, 1])
        
        # Generate input data
        input_lines = [
            "1",
            f"{n} {m}",
            " ".join(map(str, p)),
            " ".join(map(str, h))
        ]
        input_lines.extend(f"{u} {v}" for u, v in edges)
        input_str = "\n".join(input_lines) + "\n"
        
        # Solve to get expected answer
        expected = 'YES' if self.solve_happiness(input_str) else 'NO'
        return {
            "n": n, "m": m, "p": p, "h": h,
            "edges": edges, "expected_answer": expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges_str = "\n".join(f"{u} {v}" for u, v in question_case["edges"])
        prompt = f"""Determine if the happiness indexes are possible. Follow the input format:

Cities: {question_case['n']}
People: {question_case['m']}
Population: {' '.join(map(str, question_case['p']))}
Cunclebogdanandcountryhappiness: {' '.join(map(str, question_case['h']))}
Edges:
{edges_str}

Output YES or NO within [answer]...[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def solve_happiness(self, input_str):
        from io import StringIO
        import sys
        old_stdin = sys.stdin
        sys.stdin = StringIO(input_str)
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        main()

        output = sys.stdout.getvalue().strip().upper()
        sys.stdin = old_stdin
        sys.stdout = old_stdout
        return output == 'YES'
