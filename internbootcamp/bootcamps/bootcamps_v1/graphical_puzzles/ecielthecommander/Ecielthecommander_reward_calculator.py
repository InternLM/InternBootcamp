import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class EcielthecommanderRewardCalculator(BaseRewardCalculator):
    """Ecielthecommander奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answers = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answers:
            return None
        answer = answers[-1].strip()
        if answer.upper() == "IMPOSSIBLE!":
            return "Impossible!"
        return answer
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        validator = SolutionValidator(
            identity['n'],
            identity['edges'],
            solution
        )
        return validator.validate()
    
    # 其他额外方法

