import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class EmatchingvsindependentsetInstructionGenerator(BaseInstructionGenerator):
    """Ematchingvsindependentset Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=50):
        """
        初始化Ematchingvsindependentset指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        solution_type = random.choice(['Matching', 'IndSet'])
        n = random.randint(1, self.max_n)
        
        if solution_type == 'Matching':
            vertices = list(range(1, 3 * n + 1))
            random.shuffle(vertices)
            core_edges = [(vertices[i*2], vertices[i*2+1]) for i in range(n)]
            
            remaining = list(set(vertices) - {u for edge in core_edges for u in edge})
            other_edges = []
            for _ in range(min(self.max_m - n, (len(remaining)*(len(remaining)-1))//2)):
                if len(remaining) < 2: break
                u, v = random.sample(remaining, 2)
                other_edges.append((u, v))
            
            edges = core_edges + other_edges
        else:
            ind_set = list(range(2*n + 1, 3*n + 1))
            vertices = list(range(1, 2*n + 1))
            random.shuffle(vertices)
            
            core_edges = [(vertices[i*2], vertices[i*2+1]) for i in range(n-1)]
            used_vertices = {u for edge in core_edges for u in edge}
            
            remaining = [v for v in vertices if v not in used_vertices]
            other_edges = []
            for _ in range(self.max_m - (n-1)):
                if len(remaining) < 2: break
                u = random.choice(remaining)
                candidates = [v for v in remaining if v != u]
                if not candidates: break
                v = random.choice(candidates)
                other_edges.append((u, v))
            
            edges = core_edges + other_edges
            edges = [e for e in edges if not (e[0] in ind_set and e[1] in ind_set)]
        
        edges = list({tuple(sorted(e)) for e in edges if e[0] != e[1]})[:self.max_m]
        return {'n': n, 'm': len(edges), 'edges': edges}
    
    @staticmethod
    def prompt_func(question_case):
        edge_list = '\n'.join([f"{i+1}: {u} {v}" for i, (u, v) in enumerate(question_case['edges'])])
        return f"""Given a graph with {3*question_case['n']} vertices and {question_case['m']} edges. 
Find either:
1. {question_case['n']} edge matching (no shared vertices) OR 
2. {question_case['n']} vertex independent set (no connected vertices)

Formatted answer required between [answer] and [/answer]:
[answer]
Matching
1 3  # Example edge indices
[/answer] or
[answer]
IndSet
2 4  # Example vertex numbers
[/answer]

Current graph:
{edge_list}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

