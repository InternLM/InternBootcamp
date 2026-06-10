import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import defaultdict
from collections import deque
import random
import re




class CjeremybearimyInstructionGenerator(BaseInstructionGenerator):
    """Cjeremybearimy Bootcamp指令生成器"""
    
    def __init__(self, k_min=1, k_max=3, min_weight=1, max_weight=10**6):
        """
        初始化Cjeremybearimy指令生成器
        
        Args:
            k_min: 参数描述
            k_max: 参数描述
            min_weight: 参数描述
            max_weight: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.k_min = k_min
        self.k_max = k_max
        self.min_weight = min_weight
        self.max_weight = max_weight
    
    def case_generator(self):
        """使用Prim算法生成合法的随机树，确保全连接"""
        k = random.randint(self.k_min, self.k_max)
        n = 2 * k
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        
        # 使用Prim算法生成树
        visited = set([nodes[0]])
        edges = []
        candidates = []
        
        # 初始化候选边
        current = nodes[0]
        for node in nodes[1:]:
            candidates.append((current, node))
        
        while len(visited) < n:
            # 随机选择一条连接已访问和未访问节点的边
            random.shuffle(candidates)
            found = False
            for i in range(len(candidates)):
                u, v = candidates[i]
                if (u in visited) ^ (v in visited):
                    weight = random.randint(self.min_weight, self.max_weight)
                    edges.append([u, v, weight] if u < v else [v, u, weight])
                    new_node = v if u in visited else u
                    visited.add(new_node)
                    # 添加新候选边
                    for node in nodes:
                        if node not in visited:
                            candidates.append((new_node, node))
                    del candidates[i]
                    found = True
                    break
            if not found and len(visited) < n:
                # 处理不连通情况（理论上不会发生）
                unvisited = list(set(nodes) - visited)
                u = random.choice(list(visited))
                v = random.choice(unvisited)
                weight = random.randint(self.min_weight, self.max_weight)
                edges.append([u, v, weight])
                visited.add(v)

        return {
            'k': k,
            'edges': sorted(edges, key=lambda x: (x[0], x[1]))
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [str(question_case['k'])] + [
            f"{u} {v} {t}" for u, v, t in question_case['edges']
        ]
        input_str = "1\n" + "\n".join(input_lines)

        return f"""Welcome to The Medium Place! Your task is to compute G (minimum possible sum) and B (maximum possible sum) for soulmate pairs.

Problem Description:
- Assign 2k people into 2k houses arranged in a tree structure
- Each road has travel time t_i
- Soulmates must be assigned to two different houses
- Calculate sum of path times between all pairs:
  G: Minimum possible sum
  B: Maximum possible sum

Input:
{input_str}

Format your answer as: [answer]G B[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def calculate_GB(cls, k, edges):
        n = 2 * k
        adj = defaultdict(list)
        for u, v, t in edges:
            adj[u].append((v, t))
            adj[v].append((u, t))

        # BFS建立父子关系
        par = [0] * (n + 1)
        cst = [0] * (n + 1)
        q = deque([1])
        par[1] = -1  # 根节点无父

        while q:
            u = q.popleft()
            for v, t in adj[u]:
                if par[v] == 0 and v != par[u]:
                    par[v] = u
                    cst[v] = t
                    q.append(v)

        # 后序遍历计算子树大小
        dp = [1] * (n + 1)
        stack = []
        visited = [False] * (n + 1)
        stack.append((1, False))

        while stack:
            node, processed = stack.pop()
            if processed:
                for v, _ in adj[node]:
                    if v != par[node] and par[v] == node:
                        dp[node] += dp[v]
                continue
            if visited[node]:
                continue
            visited[node] = True
            stack.append((node, True))
            # 子节点逆序入栈保证处理顺序
            children = [v for v, _ in adj[node] if v != par[node] and par[v] == node]
            for child in reversed(children):
                stack.append((child, False))

        mn = mx = 0
        for v in range(2, n + 1):
            mn += cst[v] * (dp[v] % 2)
            mx += cst[v] * min(dp[v], n - dp[v])

        return mn, mx
