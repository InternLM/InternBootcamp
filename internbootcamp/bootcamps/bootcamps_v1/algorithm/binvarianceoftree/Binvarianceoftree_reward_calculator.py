import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def check_permutation_solution(n, p_list_1based):
    if n == 0:
        return (False, [])
    p_list = [x - 1 for x in p_list_1based]  # Convert to 0-based
    was = [False] * n
    cyc = defaultdict(list)

    # Find all cycles
    for i in range(n):
        if was[i]:
            continue
        cycle = []
        j = i
        while not was[j]:
            was[j] = True
            cycle.append(j)
            j = p_list[j]
        cyc[len(cycle)].append(cycle)
    
    lengths = sorted(cyc.keys(), reverse=True)
    parent = {}
    roots = []
    
    # Determine parents for each cycle length
    for l in lengths:
        found = False
        for m in lengths:
            if m < l and l % m == 0:
                parent[l] = m
                found = True
                break
        if not found:
            parent[l] = None
            roots.append(l)
    
    # Check validity of roots
    if len(roots) > 1 or (len(roots) == 1 and roots[0] > 2):
        return (False, None)
    
    # Construct the tree edges
    edges = []
    if roots:
        root_len = roots[0]
    else:
        return (False, None)
    
    # Handle root cycle(s)
    if root_len == 2:
        root_cycle = cyc[2][0]
        edges.append((root_cycle[0], root_cycle[1]))
        for cycle in cyc[2][1:]:
            edges.append((root_cycle[0], cycle[0]))
            edges.append((root_cycle[1], cycle[1]))
    elif root_len == 1 and 1 in cyc:
        main_node = cyc[1][0][0]
        for cycle in cyc[1][1:]:
            edges.append((main_node, cycle[0]))
    
    # Attach other cycles to their parents
    for l in lengths:
        if l == root_len:
            continue
        if l not in parent:
            continue
        parent_len = parent[l]
        if parent_len is None:
            continue
        parent_cycles = cyc[parent_len]
        for cycle in cyc[l]:
            for i in range(len(cycle)):
                parent_node = parent_cycles[0][i % parent_len]
                edges.append((parent_node, cycle[i]))
    
    # Convert edges back to 1-based
    edges_1based = [(u + 1, v + 1) for u, v in edges]
    return (True, edges_1based)


class BinvarianceoftreeRewardCalculator(BaseRewardCalculator):
    """Binvarianceoftree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        return last_answer
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        exists = identity['exists']
        lines = solution.strip().split('\n')
        if not lines:
            return False
        
        first_line = lines[0].strip().upper()
        if exists and first_line != 'YES':
            return False
        if not exists and first_line != 'NO':
            return False
        if not exists:
            return True
        
        n = identity['n']
        p = identity['p']
        edges = []
        edge_lines = lines[1:] if len(lines) > 1 else []
        if len(edge_lines) != n - 1:
            return False
        
        for line in edge_lines:
            parts = line.strip().split()
            if len(parts) != 2:
                return False
            try:
                u = int(parts[0])
                v = int(parts[1])
            except ValueError:
                return False
            edges.append((u, v))
        
        # Check tree validity
        parent = list(range(n + 1))
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        
        for u, v in edges:
            if u < 1 or u > n or v < 1 or v > n:
                return False
            pu, pv = find(u), find(v)
            if pu == pv:
                return False
            parent[pv] = pu
        
        root = find(1)
        for node in range(2, n + 1):
            if find(node) != root:
                return False
        
        # Check permutation invariance
        original_edges = set(frozenset((u, v)) for u, v in edges)
        permuted_edges = set()
        for u, v in edges:
            pu = p[u - 1]
            pv = p[v - 1]
            permuted_edges.add(frozenset((pu, pv)))
        
        return original_edges == permuted_edges
    
    # 其他额外方法

