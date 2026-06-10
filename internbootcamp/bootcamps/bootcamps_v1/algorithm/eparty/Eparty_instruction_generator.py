import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque
import re




class EpartyInstructionGenerator(BaseInstructionGenerator):
    """Eparty Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Eparty指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {'n': n}
    
    def case_generator(self):
        n = self.params['n']
        edges = self._generate_connected_graph(n)
        return {
            'n': n,
            'm': len(edges),
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        edges = question_case['edges']
        edges_str = '\n'.join(f"{u} {v}" for u, v in edges)
        
        return f"""You are at a party organized by Arseny. The goal is to help him introduce all guests to each other with the minimum number of steps. The process is: in each step, select a guest who will pairwise introduce all their current friends. After this step, all pairs of their friends become friends. This continues until all pairs are friends.

Input:
{n} {m}
{edges_str}

Your task is to determine the minimal number of steps and the sequence of guest IDs to select. 

Format your answer as:
[answer]
<number_of_steps>
<space_separated_guest_ids>
[/answer]

Example:
[answer]
1
1
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_connected_graph(n):
        edges = set()
        nodes = list(range(1, n+1))
        random.shuffle(nodes)

        # Generate a spanning tree
        for i in range(1, n):
            j = random.randint(0, i-1)
            u, v = sorted((nodes[j], nodes[i]))
            edges.add((u, v))

        # Add additional edges
        all_edges = [(u, v) for u in range(1, n+1) for v in range(u+1, n+1)]
        remaining = [e for e in all_edges if e not in edges]
        max_possible = n * (n-1) // 2
        m = random.randint(n-1, max_possible)
        edges.update(random.sample(remaining, k=m - (n-1)))

        return sorted(edges)

    @staticmethod
    def _solve_min_steps(n, edges):
        edges_list = [(u, v) for u in range(1, n+1) for v in range(u+1, n+1)]
        edge_to_bit = {e: i for i, e in enumerate(edges_list)}

        initial_mask = 0
        for u, v in edges:
            initial_mask |= 1 << edge_to_bit[(u, v) if u < v else (v, u)]

        target = (1 << len(edges_list)) - 1
        if initial_mask == target:
            return 0

        visited = {initial_mask: 0}
        queue = deque([(initial_mask, 0)])

        while queue:
            mask, steps = queue.popleft()

            for a in range(1, n+1):
                friends = set()
                for u in range(1, n+1):
                    if u == a:
                        continue
                    e = tuple(sorted((a, u)))
                    if mask & (1 << edge_to_bit[e]):
                        friends.add(u)

                friends.add(a)
                new_mask = mask
                for i in friends:
                    for j in friends:
                        if i < j:
                            new_mask |= 1 << edge_to_bit[(i, j)]

                if new_mask == target:
                    return steps + 1
                if new_mask not in visited or steps + 1 < visited[new_mask]:
                    visited[new_mask] = steps + 1
                    queue.append((new_mask, steps + 1))

        return n  # Fallback
