import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class FmaxmexInstructionGenerator(BaseInstructionGenerator):
    """Fmaxmex Bootcamp指令生成器"""
    
    def __init__(self, max_nodes=6, q_max=4):
        """
        初始化Fmaxmex指令生成器
        
        Args:
            max_nodes: 参数描述
            q_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_nodes = max_nodes  # 限制节点数提高计算可靠性
        self.q_max = q_max
    
    def case_generator(self):
        n = random.randint(2, self.max_nodes)
        p = list(range(n))
        random.shuffle(p)
        d, parent_map = self._build_tree(n)
        
        queries = []
        expected = []
        current_p = p.copy()
        
        for _ in range(random.randint(1, self.q_max)):
            if random.random() < 0.4 and len(queries) > 0:
                i, j = random.sample(range(1, n+1), 2)
                queries.append({'type': 1, 'i': i, 'j': j})
                current_p[i-1], current_p[j-1] = current_p[j-1], current_p[i-1]
            else:
                queries.append({'type': 2})
                expected.append(self._calc_mex(n, current_p, parent_map))
        
        return {
            'n': n,
            'p': current_p,
            'd': d,
            'queries': queries,
            'expected_answers': expected,
            'parent_map': parent_map
        }
    
    @staticmethod
    def prompt_func(case):
        prompt = f"""Tree with {case['n']} nodes (root=1)
Permutation: {case['p']}
Parent list (nodes 2-{case['n']}): {case['d']}
Queries:
"""
        for i, q in enumerate(case['queries'], 1):
            if q['type'] == 1:
                prompt += f"{i}. Swap nodes {q['i']} and {q['j']}\n"
            else:
                prompt += f"{i}. Find max MEX\n"
        return prompt + "\nAnswer each type 2 query with [answer]number[/answer]" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _build_tree(self, n):
        parent_map = {1: None}
        for i in range(2, n+1):
            parent_map[i] = random.randint(1, i-1)
        return [parent_map[i] for i in range(2, n+1)], parent_map

    @staticmethod
    def _find_lca(u, v, parent_map):
        path = set()
        while u:
            path.add(u)
            u = parent_map.get(u)
        while v not in path:
            v = parent_map.get(v)
        return v

    def _calc_mex(self, n, p, parent_map):
        max_mex = 0
        for start in range(1, n+1):
            for end in range(start, n+1):
                path = set()
                current = start
                lca = self._find_lca(start, end, parent_map)

                while current != lca:
                    path.add(current)
                    current = parent_map[current]
                path.add(lca)

                current = end
                while current != lca:
                    path.add(current)
                    current = parent_map[current]

                values = {p[node-1] for node in path}
                mex = 0
                while mex in values:
                    mex += 1
                max_mex = max(max_mex, mex)
        return max_mex
