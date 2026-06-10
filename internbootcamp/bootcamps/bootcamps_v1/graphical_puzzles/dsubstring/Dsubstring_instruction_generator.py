import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict




class DsubstringInstructionGenerator(BaseInstructionGenerator):
    """Dsubstring Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dsubstring指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.m = params.get('m', 4)
        self.seed = params.get('seed', None)
        if self.seed is not None:
            random.seed(self.seed)
    
    def case_generator(self):
        n = self.n
        m = self.m
        
        # 生成每个节点的字母
        letters = [chr(random.randint(ord('a'), ord('z'))) for _ in range(n)]
        s = ''.join(letters)
        
        # 生成m条有向边
        edges = []
        for _ in range(m):
            x = random.randint(1, n)
            y = random.randint(1, n)
            edges.append( (x, y) )
        
        # 检查图中是否存在环
        edges_0based = [ (x-1, y-1) for x, y in edges ]
        if self.has_cycle(n, edges_0based):
            correct_answer = -1
        else:
            # 计算最长路径的值
            correct_answer = self.compute_max_path(n, edges_0based, letters)
        
        # 将edges转换为1-based的字符串表示
        edges_str = [[str(x), str(y)] for x, y in edges]
        
        case = {
            'n': n,
            'm': m,
            's': s,
            'edges': edges_str,
            'correct_answer': correct_answer
        }
        
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        s = question_case['s']
        edges = question_case['edges']
        
        edge_lines = '\n'.join([f"{x} {y}" for x, y in edges])
        
        prompt = f"""You are given a graph with {n} nodes and {m} directed edges. Each node is assigned a lowercase letter, as follows: {s}.

The directed edges are:
{edge_lines}

The value of a path is defined as the highest frequency of any single letter along that path. For example, a path with letters 'abaca' has a value of 3 because 'a' appears three times.

Your task is to determine the maximum possible value of any path in this graph. If the graph contains a cycle, making the path infinitely long, output -1. Otherwise, output the maximum value.

Please provide your answer within [answer] tags.
"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def has_cycle(self, n, edges):
        adj = [[] for _ in range(n)]
        in_degree = [0] * n
        for u, v in edges:
            adj[u].append(v)
            in_degree[v] += 1

        queue = deque()
        for i in range(n):
            if in_degree[i] == 0:
                queue.append(i)

        count = 0
        while queue:
            u = queue.popleft()
            count += 1
            for v in adj[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        return count != n

    def compute_max_path(self, n, edges, letters):
        E = defaultdict(list)
        P = defaultdict(list)
        C = [0] * n

        for u, v in edges:
            E[u].append(v)
            P[v].append(u)
            C[u] += 1

        leafs = [u for u in E if len(E[u]) == 0]

        if not leafs:
            return -1

        DP = [ [0]*27 for _ in range(n) ]
        for i in range(n):
            c = ord(letters[i]) - ord('a')
            DP[i][c] = 1

        Q = deque(leafs)
        used = [False] * n

        while Q:
            u = Q.popleft()
            if used[u]:
                continue
            used[u] = True

            for c in range(27):
                max_val = 0
                for v in E[u]:
                    if DP[v][c] > max_val:
                        max_val = DP[v][c]
                DP[u][c] += max_val

            for v in P[u]:
                C[v] -= 1
                if C[v] == 0:
                    Q.append(v)

        if any(c > 0 for c in C):
            return -1
        else:
            max_value = max(max(row) for row in DP)
            return max_value
