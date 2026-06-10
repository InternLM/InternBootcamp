import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class DlunarnewyearandawanderInstructionGenerator(BaseInstructionGenerator):
    """Dlunarnewyearandawander Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dlunarnewyearandawander指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.m = params.get('m', self.n)
        if self.m < self.n-1:
            raise ValueError(f"m must be ≥ n-1 ({self.n-1}), got {self.m}")
        if self.n < 1:
            raise ValueError(f"n must be ≥ 1, got {self.n}")
    
    def case_generator(self):
        n = self.n
        m = self.m
        edges = []
        visited = {1}
        unvisited = set(range(2, n+1))
        
        # 生成生成树确保连通性
        while unvisited:
            u = random.choice(list(unvisited))
            v = random.choice(list(visited))
            edges.append((v, u))
            visited.add(u)
            unvisited.remove(u)
        
        # 生成剩余边（允许自环和重复）
        for _ in range(m - (n-1)):
            u = random.randint(1, n)
            v = random.randint(1, n)
            edges.append((u, v))
        
        # 洗牌避免边顺序影响生成结果
        random.shuffle(edges)
        return {
            'n': n,
            'm': m,
            'edges': edges,
            'correct_answer': compute_min_lex_sequence(n, edges)
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges = [" ".join(map(str, e)) for e in question_case['edges']]
        input_str = f"{question_case['n']} {question_case['m']}\n" + "\n".join(edges)
        return f"""作为公园路径规划AI，你需要找到字典序最小的节点访问序列。规则：

1. 从节点1出发并记录
2. 每次访问新节点立即记录
3. 使用双向通道移动
4. 序列字典序最小标准：首个不同位置数值更小则更优

输入格式：
n m
u1 v1
...
um vm

当前输入：
{input_str}

答案格式：[answer]1 3 2 ...[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

