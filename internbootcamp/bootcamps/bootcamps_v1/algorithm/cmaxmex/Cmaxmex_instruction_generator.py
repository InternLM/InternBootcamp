import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CmaxmexInstructionGenerator(BaseInstructionGenerator):
    """Cmaxmex Bootcamp指令生成器"""
    
    def __init__(self, max_n=6, max_q=5, **params):
        """
        初始化Cmaxmex指令生成器
        
        Args:
            max_n: 参数描述
            max_q: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.max_n = max_n
        self.max_q = max_q
    
    def case_generator(self):
        n = random.randint(2, self.max_n)
        # Generate tree structure
        d = []
        parent = {}
        for i in range(2, n + 1):
            possible_parents = list(range(1, i))
            di = random.choice(possible_parents)
            d.append(di)
            parent[i] = di
        # Generate permutation p
        p = list(range(n))
        random.shuffle(p)
        # Generate queries
        q = random.randint(1, self.max_q)
        current_p = p.copy()
        queries = []
        for _ in range(q):
            query_type = random.choices([1, 2], weights=[0.3, 0.7], k=1)[0]
            if query_type == 1:
                i = random.randint(1, n)
                j = random.randint(1, n)
                while i == j:
                    j = random.randint(1, n)
                queries.append({'type': 1, 'i': i, 'j': j})
                # Swap p values
                current_p[i-1], current_p[j-1] = current_p[j-1], current_p[i-1]
            else:
                # Compute current max MEX
                max_mex = 0
                for u in range(1, n + 1):
                    for v in range(u, n + 1):
                        path = self.get_path(u, v, parent)
                        values = {current_p[node-1] for node in path}
                        mex = self.compute_mex(values)
                        if mex > max_mex:
                            max_mex = mex
                queries.append({'type': 2, 'answer': max_mex})
        return {
            'n': n,
            'p': p,
            'd': d,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        p = ' '.join(map(str, question_case['p']))
        d = ' '.join(map(str, question_case['d']))
        queries = []
        for q in question_case['queries']:
            if q['type'] == 1:
                queries.append(f"1 {q['i']} {q['j']}")
            else:
                queries.append("2")
        input_str = (
            f"{n}\n{p}\n{d}\n{len(queries)}\n" + '\n'.join(queries)
        )
        prompt = f"""给定一个以节点1为根的树，每个节点包含唯一的0到{n-1}的数值。处理以下两种查询：
1. 交换两个节点的数值。
2. 查询所有路径中MEX的最大值。

输入格式：
- 首行：节点数n
- 第二行：各节点的初始数值p_1到p_n
- 第三行：节点2到n的父节点列表
- 第四行：查询数q
- 接下来q行：每个查询的描述（类型1为交换操作，类型2为查询）

请处理所有查询，并将类型2查询的结果按顺序放入[answer]标签中。例如：
[answer]
3
2
[/answer]

输入数据：
{input_str}

请根据上述输入，给出所有类型2查询的结果："""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def get_lca(u, v, parent):
        ancestors = set()
        current = u
        while current is not None:
            ancestors.add(current)
            current = parent.get(current, None)
        current = v
        while current is not None and current not in ancestors:
            current = parent.get(current, None)
        return current if current is not None else 1

    @classmethod
    def get_path(cls, u, v, parent):
        lca = cls.get_lca(u, v, parent)
        path_u = []
        current = u
        while current != lca:
            path_u.append(current)
            current = parent.get(current, None)
        path_u.append(lca)
        # Get v to lca path
        path_v = []
        current = v
        while current != lca:
            path_v.append(current)
            current = parent.get(current, None)
        # Combine paths
        return path_u + path_v[::-1]

    @staticmethod
    def compute_mex(s):
        mex = 0
        while mex in s:
            mex += 1
        return mex
