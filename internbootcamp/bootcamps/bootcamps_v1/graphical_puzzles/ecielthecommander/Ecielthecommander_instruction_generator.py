import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def generate_tree(n):
    """Generate a random tree using Prüfer sequence with shuffled node labels."""
    if n == 1: return []
    labels = list(range(1, n+1))
    random.shuffle(labels)
    
    if n == 2: return [(labels[0], labels[1])]
    
    prufer = [random.randint(0, n-2) for _ in range(n-2)]
    node_count = [0] * n
    for node in prufer: node_count[node] += 1
    
    edges = []
    leaf = None
    for node in prufer:
        if leaf is None:
            for i in range(n):
                if node_count[i] == 0 and i != node:
                    leaf = i
                    break
        edges.append((leaf, node))
        node_count[leaf] = -1
        node_count[node] -= 1
        if node_count[node] == 0 and leaf > node:
            leaf = node
        else:
            leaf = None
    
    last_nodes = [i for i in range(n) if node_count[i] != -1]
    edges.append((last_nodes[0], last_nodes[1]))
    
    return [(labels[a], labels[b]) for a, b in edges]



# === 源文件中的其他类 ===

class SolutionValidator:
    def __init__(self, n, edges, solution):
        self.n = n
        self.adj = [[] for _ in range(n+1)]
        for a, b in edges:
            self.adj[a].append(b)
            self.adj[b].append(a)
        self.rank = solution.split() if solution != "Impossible!" else []
        self.parent = [0]*(n+1)
        self.depth = [0]*(n+1)
        self._build_lca(1, 0)

    def _build_lca(self, u, p):
        stack = [(u, p, False)]
        while stack:
            u, p, visited = stack.pop()
            if visited:
                for v in self.adj[u]:
                    if v != p and v != self.parent[v]:
                        self.depth[v] = self.depth[u] + 1
                        self.parent[v] = u
            else:
                stack.append((u, p, True))
                for v in self.adj[u]:
                    if v != p:
                        stack.append((v, u, False))

    def _lca(self, u, v):
        while u != v:
            if self.depth[u] > self.depth[v]:
                u = self.parent[u]
            else:
                v = self.parent[v]
        return u

    def validate(self):
        if self.rank == ["Impossible!"]:
            return self._validate_impossible()
        
        if len(self.rank) != self.n:
            return False
        ranks = {}
        for i, r in enumerate(self.rank):
            if len(r) != 1 or not r.isupper():
                return False
            ranks[i+1] = r

        # Check all pairs with same rank
        rank_map = defaultdict(list)
        for node in range(1, self.n+1):
            rank_map[ranks[node]].append(node)

        for r, nodes in rank_map.items():
            if len(nodes) < 2: 
                continue
            # Check all pairs
            for i in range(len(nodes)):
                for j in range(i+1, len(nodes)):
                    a, b = nodes[i], nodes[j]
                    lca = self._lca(a, b)
                    path = []
                    while a != lca:
                        path.append(a)
                        a = self.parent[a]
                    path.append(lca)
                    temp = []
                    while b != lca:
                        temp.append(b)
                        b = self.parent[b]
                    path += reversed(temp)
                    # Check path
                    has_higher = False
                    for node in path:
                        if ranks[node] < r:
                            has_higher = True
                            break
                    if not has_higher:
                        return False
        return True

    def _validate_impossible(self):
        try:
            gen = SolutionGenerator(self.n, self.adj[1:])
            solution = gen.generate()
            return solution == "Impossible!"
        except:
            return False


class EcielthecommanderInstructionGenerator(BaseInstructionGenerator):
    """Ecielthecommander Bootcamp指令生成器"""
    
    def __init__(self, max_n=15, min_n=2):
        """
        初始化Ecielthecommander指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.min_n = min_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        edges = generate_tree(n)
        return {'n': n, 'edges': edges}
    
    @staticmethod
    def prompt_func(case):
        n = case['n']
        edges = case['edges']
        edge_lines = '\n'.join(f"{a} {b}" for a, b in edges)
        return f"""As the commander of Tree Land with {n} cities connected in a tree structure:
{edge_lines}

Assign A-Z ranks to each city such that:
- Any two cities with the same rank must have a higher-ranked city on their connecting path

Output format: Either "Impossible!" or {n} space-separated uppercase letters.
Enclose your final answer within [answer] and [/answer] tags.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

