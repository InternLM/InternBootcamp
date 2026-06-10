import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class BinvarianceoftreeInstructionGenerator(BaseInstructionGenerator):
    """Binvarianceoftree Bootcamp指令生成器"""
    
    def __init__(self, max_n=10):
        """
        初始化Binvarianceoftree指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # Control the size for case generation
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        p = list(range(1, n+1))
        random.shuffle(p)
        exists, edges = check_permutation_solution(n, p)
        case = {
            "n": n,
            "p": p,
            "exists": exists
        }
        if exists:
            case["edges"] = edges
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case["n"]
        p = question_case["p"]
        p_str = ' '.join(map(str, p))
        problem = (
            "You are given a permutation of size n. Your task is to determine if there exists a tree of size n that is invariant under this permutation. If it exists, output YES followed by the edges of the tree; otherwise, output NO.\n\n"
            f"Input:\n{n}\n{p_str}\n\n"
            "Output your answer as follows:\n"
            "- If no such tree exists, output: NO\n"
            "- If it exists, output: YES followed by n-1 edges, each on a new line.\n"
            "Enclose your final answer within [answer] and [/answer] tags."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

