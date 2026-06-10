import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from itertools import combinations




class AsearchingforgraphInstructionGenerator(BaseInstructionGenerator):
    """Asearchingforgraph Bootcamp指令生成器"""
    
    def __init__(self, n_min=5, n_max=24, p_min=0):
        """
        初始化Asearchingforgraph指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            p_min: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.p_min = p_min
    
    def case_generator(self):
        while True:
            n = random.randint(self.n_min, self.n_max)
            max_possible_edges = n * (n - 1) // 2
            max_p = max_possible_edges - 2 * n
            if max_p >= self.p_min:
                break
        p = random.randint(self.p_min, max_p)
        edges = self.generate_reference_edges(n, p)
        return {'n': n, 'p': p, 'edges': edges}
    
    @staticmethod
    def prompt_func(case):
        n, p = case['n'], case['p']
        example = "\n".join(f"{u} {v}" for u, v in case['edges'][:3]) + "\n..."
        return f"""Construct a {p}-interesting graph with {n} vertices. Conditions:
1. Exactly {2*n+p} edges
2. No self-loops/multi-edges
3. Any k-vertex subgraph has ≤ {2*'k'}+{p} edges

Output {2*n+p} edges in [answer]...[/answer] format.

Example (n=6, p=0):
{example}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_reference_edges(n, p):
        edges = []
        required = 2 * n + p
        for i in range(1, n+1):
            for j in range(i+1, n+1):
                edges.append((i, j))
                if len(edges) == required:
                    return edges
        return edges
