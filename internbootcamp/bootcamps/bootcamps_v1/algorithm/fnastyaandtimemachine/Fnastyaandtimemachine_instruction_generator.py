import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class FnastyaandtimemachineInstructionGenerator(BaseInstructionGenerator):
    """Fnastyaandtimemachine Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Fnastyaandtimemachine指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params.copy()
        self.params.setdefault('n', 5)
        # 确保最小节点数为1
        if self.params['n'] < 1:
            self.params['n'] = 1
    
    def case_generator(self):
        n = self.params['n']
        edges = self._generate_tree(n)
        return {'n': n, 'edges': edges}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        edge_lines = "\n".join(f"{u} {v}" for u, v in edges)
        return f"""Denis needs to visit all squares in the city and return to square 1 as quickly as possible. The city is structured as a tree with {n} squares. The squares are connected by the following roads:

Input:
{n}
{edge_lines}

Find a valid route that meets all requirements:
1. Starts at (1, 0) and ends at square 1
2. All transitions are either time jumps (same square, lower time) or road moves (adjacent square, time+1)
3. All (square, time) pairs must be unique
4. Visits all {n} squares
5. Minimizes the maximum time value

Format your answer with the route length first, then all (square, time) pairs enclosed in [answer] and [/answer] tags:

Example format for a 5-node case:
[answer]
13
1 0
2 1
3 2
3 1
2 2
4 3
4 1
5 2
5 1
4 2
2 3
2 0
1 1
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_tree(n):
        if n == 1:
            return []

        # 优化后的树生成算法
        nodes = list(range(1, n+1))
        if n == 2:
            return [(nodes[0], nodes[1])]

        # 改进的Prufer序列生成
        prufer = [random.choice(nodes) for _ in range(n-2)]
        degree = defaultdict(int)
        for node in prufer:
            degree[node] += 1

        adj = defaultdict(list)
        # 阶段1：处理Prufer序列
        for p in prufer:
            for v in nodes:
                if degree[v] == 0 and (p != v or degree[p] > 0):
                    adj[p].append(v)
                    adj[v].append(p)
                    degree[p] -= 1
                    degree[v] -= 1
                    break

        # 阶段2：处理剩余节点
        leaves = [v for v in nodes if degree[v] == 0]
        while len(leaves) >= 2:
            u = leaves.pop()
            v = leaves.pop()
            adj[u].append(v)
            adj[v].append(u)

        # 去重并排序边
        seen = set()
        edges = []
        for u in adj:
            for v in adj[u]:
                if u < v and (u, v) not in seen:
                    edges.append((u, v))
                    seen.add((u, v))
        return sorted(edges, key=lambda x: (x[0], x[1]))
