import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DhamiltonianspanningtreeInstructionGenerator(BaseInstructionGenerator):
    """Dhamiltonianspanningtree Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, **params):
        """
        初始化Dhamiltonianspanningtree指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.params = params
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        edges = []
        # Generate a random spanning tree using parent assignment method
        for i in range(2, n + 1):
            parent = random.randint(1, i - 1)
            edges.append([i, parent])
        x = random.randint(1, 10)
        y = random.randint(1, 10)
        # Build adjacency list (0-based)
        graph = [[] for _ in range(n)]
        for u, v in edges:
            u0 = u - 1
            v0 = v - 1
            graph[u0].append(v0)
            graph[v0].append(u0)
        # Calculate correct answer based on reference solution logic
        if x >= y:
            has_center = any(len(adj) == n - 1 for adj in graph)
            correct = x + y * (n - 2) if has_center else y * (n - 1)
        else:
            track = self.dfs(graph)
            track.reverse()
            maxans = [[0, 0] for _ in range(n)]
            for curr, prev in track:
                summ = 0
                goodcnt = 0
                for neighbor in graph[curr]:
                    if neighbor != prev:
                        summ += maxans[neighbor][0]
                        if maxans[neighbor][1]:
                            goodcnt += 1
                maxans[curr][0] = summ + min(2, goodcnt)
                maxans[curr][1] = 0 if goodcnt >= 2 else 1
            ans = maxans[0][0]
            correct = x * ans + y * (n - 1 - ans)
        return {
            'n': n,
            'x': x,
            'y': y,
            'edges': edges,
            'correct_answer': correct
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        x = question_case['x']
        y = question_case['y']
        edges = question_case['edges']
        edge_list = '\n'.join([f"{u} {v}" for u, v in edges])
        return f"""你是一个专业的算法竞赛选手，需要解决以下问题：

**题目背景**

{n}个城市通过道路网络相连。每对城市之间都有一条双向道路，总共有{n*(n-1)//2}条路。初始所有道路通行时间为{y}秒。之后选定了其中一棵生成树（即连接所有城市的{n-1}条无环路），树中的道路通行时间被改为{x}秒。

**任务**

找到一条访问所有城市恰好一次的最短路径，并计算其总时间。

**输入格式**

第一行：三个整数n, x, y（2 ≤ n ≤ 2e5）
随后{n-1}行：每行两个整数表示生成树中的边

**输入实例**

{n} {x} {y}
{edge_list}

**输出格式**

一个整数表示最短时间，确保答案在[answer]标签内，如：[answer]123[/answer]。

请给出答案：""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def dfs(graph, start=0):
        track = [[start, -1]]
        stack = [start]
        visited = [0] * len(graph)  # 0: unprocessed, -1: processed
        while stack:
            curr = stack[-1]
            if visited[curr] >= len(graph[curr]):
                visited[curr] = -1
                stack.pop()
            else:
                neighbor_idx = visited[curr]
                neighbor = graph[curr][neighbor_idx]
                visited[curr] += 1
                if visited[neighbor] == 0:
                    stack.append(neighbor)
                    track.append([neighbor, curr])
        return track
