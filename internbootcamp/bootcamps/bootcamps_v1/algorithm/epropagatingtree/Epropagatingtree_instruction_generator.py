import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import deque




class EpropagatingtreeInstructionGenerator(BaseInstructionGenerator):
    """Epropagatingtree Bootcamp指令生成器"""
    
    def __init__(self, n=5, m=5):
        """
        初始化Epropagatingtree指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
    
    def case_generator(self):
        n = self.n
        edges, parent = self.generate_tree(n)
        level = self.compute_levels(parent, n)
        children = self.build_children_dict(parent)
        subtree_nodes = {x: self.get_subtree_nodes(x, children) for x in range(1, n+1)}
        initial_a = [random.randint(1, 1000) for _ in range(n)]
        
        current_values = initial_a.copy()
        values_history = [current_values.copy()]
        queries = []
        correct_outputs = []
        
        # Generate all queries first
        for _ in range(self.m):
            if len(correct_outputs) < self.m // 2 or random.random() < 0.5:
                # Generate type 1 query
                x = random.randint(1, n)
                val = random.randint(1, 1000)
                queries.append(('1', x, val))
                
                # Record state before applying
                values_history.append(current_values.copy())
                # Apply changes
                x_level = level[x]
                for y in subtree_nodes[x]:
                    delta = val * ((-1) ** (level[y] - x_level))
                    current_values[y-1] += delta
            else:
                # Generate type 2 query
                x = random.randint(1, n)
                queries.append(('2', x))
                correct_outputs.append(current_values[x-1])
                values_history.append(current_values.copy())
        
        # Ensure at least one type 2 query and correct outputs
        if not correct_outputs:
            # Find last type 1 query to replace
            for i in reversed(range(len(queries))):
                if queries[i][0] == '1':
                    # Get state before this query
                    prev_values = values_history[i]
                    x = random.randint(1, n)
                    # Replace with type 2 query
                    queries[i] = ('2', x)
                    correct_outputs.insert(i - sum(1 for q in queries[:i] if q[0] == '2'), prev_values[x-1])
                    break
        
        # Format queries to strings
        formatted_queries = []
        for q in queries:
            if q[0] == '1':
                formatted_queries.append(f'1 {q[1]} {q[2]}')
            else:
                formatted_queries.append(f'2 {q[1]}')
        
        case = {
            'n': n,
            'm': self.m,
            'a': initial_a,
            'edges': [[u, v] for u, v in edges],
            'queries': formatted_queries,
            'correct_outputs': correct_outputs
        }
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [
            f"{question_case['n']} {question_case['m']}",
            ' '.join(map(str, question_case['a']))
        ]
        input_lines += [' '.join(map(str, e)) for e in question_case['edges']]
        input_lines += question_case['queries']
        joined_input = '\n'.join(input_lines)
        
        problem_text = f"""Iahub discovered a propagating tree with a special property. When a value is added to a node, it propagates to children with alternating signs. 

You must process the following queries and output answers for type 2 queries. Format each answer on a separate line within [answer] and [/answer] tags.

Input:
{joined_input}

Provide your answers for type 2 queries in order, each enclosed in [answer] tags:"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_tree(n):
        if n == 1:
            return [], {1: None}
        parent = {1: None}
        edges = []
        available = [1]
        for i in range(2, n+1):
            p = random.choice(available)
            parent[i] = p
            edges.append((p, i))
            available.append(i)
        return edges, parent

    @staticmethod
    def compute_levels(parent, n):
        level = {1: 0}
        for i in range(2, n+1):
            level[i] = level[parent[i]] + 1
        return level

    @staticmethod
    def build_children_dict(parent):
        children = {}
        for child in parent:
            p = parent.get(child)
            if p is not None:
                children.setdefault(p, []).append(child)
        return children

    @staticmethod
    def get_subtree_nodes(x, children):
        subtree = []
        stack = [x]
        while stack:
            node = stack.pop()
            subtree.append(node)
            stack.extend(reversed(children.get(node, [])))  # Maintain order
        return subtree
