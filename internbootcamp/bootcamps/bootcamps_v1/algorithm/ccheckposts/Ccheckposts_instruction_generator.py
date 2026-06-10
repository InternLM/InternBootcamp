import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from itertools import combinations
import re




class CcheckpostsInstructionGenerator(BaseInstructionGenerator):
    """Ccheckposts Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10, cost_min=0, cost_max=100, max_scc_count=3):
        """
        初始化Ccheckposts指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            cost_min: 参数描述
            cost_max: 参数描述
            max_scc_count: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.cost_min = cost_min
        self.cost_max = cost_max
        self.max_scc_count = max_scc_count
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        max_possible_k = min(n, self.max_scc_count)
        k = random.randint(1, max_possible_k)
        s_list = self.split_n_into_k(n, k)
        nodes = list(range(1, n+1))
        scc_nodes = []
        start = 0
        for s in s_list:
            end = start + s
            scc_nodes.append(nodes[start:end])
            start = end
        
        internal_edges = []
        for scc in scc_nodes:
            s = len(scc)
            if s >= 2:
                for i in range(s):
                    u = scc[i]
                    v = scc[(i+1) % s]
                    internal_edges.append((u, v))
        
        cross_edges = []
        existing_edges = set(internal_edges)
        for i in range(len(scc_nodes)):
            for j in range(i+1, len(scc_nodes)):
                if random.random() < 0.3:
                    u = random.choice(scc_nodes[i])
                    v = random.choice(scc_nodes[j])
                    if (u, v) not in existing_edges and u != v:
                        cross_edges.append((u, v))
                        existing_edges.add((u, v))
        
        edges = internal_edges + cross_edges
        m = len(edges)
        
        costs = []
        for scc in scc_nodes:
            min_cost = random.randint(self.cost_min, self.cost_max)
            num_min = random.randint(1, len(scc))
            selected = random.sample(scc, num_min)
            for node in scc:
                if node in selected:
                    costs.append(min_cost)
                else:
                    costs.append(min_cost + random.randint(1, 10))
        
        return {
            'n': n,
            'costs': costs,
            'm': m,
            'edges': edges,
            'scc_list': scc_nodes
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [
            str(question_case['n']),
            ' '.join(map(str, question_case['costs'])),
            str(question_case['m'])
        ] + [f"{u} {v}" for u, v in question_case['edges']]
        input_text = '\n'.join(input_lines)
        prompt = f"""As the mayor, you need to secure all junctions with minimum cost. Each checkpost can protect reachable junctions. Find the minimal total cost and number of ways (mod 1e9+7).

Input:
{input_text}

Output two integers: minimal cost and number of ways. Place your answer within [answer] and [/answer], e.g., [answer]15 6[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def split_n_into_k(self, n, k):
        if k == 1:
            return [n]
        dividers = sorted(random.sample(range(1, n), k-1))
        prev = 0
        parts = []
        for d in dividers:
            parts.append(d - prev)
            prev = d
        parts.append(n - prev)
        return parts
