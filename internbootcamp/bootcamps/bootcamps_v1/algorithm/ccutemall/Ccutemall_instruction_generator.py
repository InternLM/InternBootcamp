import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcutemallInstructionGenerator(BaseInstructionGenerator):
    """Ccutemall Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=20, **kwargs):
        """
        初始化Ccutemall指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 2)
        self.n_max = n_max
    
    def case_generator(self):
        """优化的案例生成逻辑"""
        while True:
            n = random.randint(self.n_min, self.n_max)
            edges = self.generate_tree(n)
            
            try:
                correct_k = self._calculate_solution(n, edges)
            except:
                continue  # 处理可能的递归深度问题
            
            # 根据奇偶性验证解的有效性
            if (n % 2 == 1 and correct_k == -1) or (n % 2 == 0 and correct_k >= 0):
                return {'n': n, 'edges': edges, 'correct_k': correct_k}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        edge_list = '\n'.join(f"{u} {v}" for u, v in edges)
        return f"""Given a tree with {n} vertices represented by undirected edges. Find the maximum number of edges that can be removed such that all resulting connected components contain an even number of vertices. If impossible, output -1.

Input Format:
n
u1 v1
...
u(n-1) v(n-1)

Current Tree Structure:
{n}
{edge_list}

Present your answer as a single integer within [answer] tags. Example: [answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_tree(self, n):
        """使用改进的Prüfer序列生成更平衡的树结构"""
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]

        # 生成更平衡的Prüfer序列
        prufer = []
        for _ in range(n-2):
            # 偏好选择中间节点
            prufer.append(random.randint(max(1, n//4), min(n, 3*n//4)))

        degree = [1]*(n+1)
        for node in prufer:
            degree[node] += 1

        edges = []
        for node in prufer:
            for v in range(1, n+1):
                if degree[v] == 1:
                    edges.append((node, v))
                    degree[node] -= 1
                    degree[v] -= 1
                    break

        # 处理剩余节点时保持随机性
        remaining = [v for v in range(1, n+1) if degree[v] == 1]
        edges.append((remaining.pop(), remaining.pop()))

        # 随机打乱边并确保节点顺序
        random.shuffle(edges)
        return [(u, v) if u < v else (v, u) for u, v in edges]

    def _calculate_solution(self, n, edges):
        """修正的DFS解法"""
        if n % 2 != 0:
            return -1

        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        self.count = 0

        def dfs(node, parent):
            size = 1
            for neighbor in adj[node]:
                if neighbor == parent:
                    continue
                child_size = dfs(neighbor, node)
                size += child_size
                if child_size % 2 == 0:
                    self.count += 1
            return size

        total_size = dfs(1, -1)
        # 验证总大小
        return self.count if total_size % 2 == 0 else -1
