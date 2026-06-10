import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from itertools import combinations




class CpartyInstructionGenerator(BaseInstructionGenerator):
    """Cparty Bootcamp指令生成器"""
    
    def __init__(self, n_min=3, n_max=8):
        """
        初始化Cparty指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 1)  # 确保n≥1
        self.n_max = n_max
    
    def case_generator(self):
        """生成保证连通性的随机图并计算最优解"""
        n = random.randint(self.n_min, self.n_max)
        edges = self._generate_connected_graph(n)
        min_steps, solution = self._calculate_optimal_solution(n, edges)
        return {
            'n': n,
            'm': len(edges),
            'edges': edges,
            'min_steps': min_steps,
            'solution': solution
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        """生成带明确格式要求的问题描述"""
        edges = '\n'.join(f"{u} {v}" for u, v in case['edges'])
        return f"""## 聚会好友问题

Arseny的聚会有{case['n']}位客人，初始好友关系如下：
{edges}

每次操作选择一位客人，使得他的所有当前好友互相成为直接好友。求达成全员互为好友所需的最少操作次数及对应选择顺序。

请按以下格式输出答案：
[answer]
步骤数
选择的客人序列（空格分隔）
[/answer]

示例：
[answer]
2
2 3
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_connected_graph(self, n):
        """改进的连通图生成算法"""
        if n == 1:
            return []

        edges = set()
        nodes = list(range(1, n+1))
        visited = {nodes[0]}
        unvisited = set(nodes[1:])

        # Prim算法生成生成树
        while unvisited:
            u = random.choice(list(visited))
            v = random.choice(list(unvisited))
            edges.add(frozenset((u, v)))
            visited.add(v)
            unvisited.remove(v)

        # 添加随机边 (至少添加n-1条边)
        all_possible = {frozenset(e) for e in combinations(nodes, 2)}
        remaining = list(all_possible - edges)
        random.shuffle(remaining)

        extra = random.randint(0, len(remaining))
        edges.update(remaining[:extra])

        return sorted([sorted(list(e)) for e in edges])

    def _calculate_optimal_solution(self, n, edges):
        """基于位运算的高效算法（参考原题解）"""
        if n == 1:
            return 0, []

        # 转换为0-based邻接表
        adj = [0] * n
        for u, v in edges:
            u_idx = u - 1
            v_idx = v - 1
            adj[u_idx] |= 1 << v_idx
            adj[v_idx] |= 1 << u_idx

        # 添加自环
        for i in range(n):
            adj[i] |= 1 << i

        # 预处理覆盖关系
        full_mask = (1 << n) - 1
        if all(mask == full_mask for mask in adj):
            return 0, []

        # 初始化neigh数组
        max_mask = 1 << n
        coverage = [0] * max_mask
        for i in range(n):
            coverage[1 << i] = adj[i]

        # 预处理所有mask的覆盖关系
        for mask in range(max_mask):
            for i in range(n):
                if (mask & (1 << i)) and (coverage[mask ^ (1 << i)] & (1 << i)):
                    coverage[mask] = coverage[mask ^ (1 << i)] | adj[i]

        # 寻找最小集合
        best_mask = full_mask
        min_steps = n
        for mask in range(max_mask):
            if coverage[mask] == full_mask:
                cnt = bin(mask).count('1')
                if cnt < min_steps:
                    min_steps = cnt
                    best_mask = mask

        solution = [i+1 for i in range(n) if (best_mask & (1 << i))]
        return min_steps, solution
