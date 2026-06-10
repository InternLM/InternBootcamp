import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from itertools import combinations




class CtreesoftranquillityInstructionGenerator(BaseInstructionGenerator):
    """Ctreesoftranquillity Bootcamp指令生成器"""
    
    def __init__(self, max_n=5):
        """
        初始化Ctreesoftranquillity指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(2, self.max_n)
        # 生成合法的树结构 [关键修正点]
        a_parents = [random.randint(1, i) for i in range(1, n)]
        b_parents = [random.randint(1, i) for i in range(1, n)]

        # 构建祖先关系字典 [增加调试日志]
        def safe_build_parents(parents):
            ancestor_dict = {1: set()}
            for node in range(2, n+1):
                path = set()
                current = parents[node-2]
                path.add(current)
                while current != 1:
                    current = parents[current-2] if current >=2 else 1
                    path.add(current)
                ancestor_dict[node] = path
            return ancestor_dict

        s_ancestors = safe_build_parents(a_parents)
        k_ancestors = safe_build_parents(b_parents)

        # 构建邻接矩阵 [变量名修正]
        adj = {u: set() for u in range(1, n+1)}
        for u in range(1, n+1):
            for v in range(1, n+1):
                if u == v: continue
                cond1 = (u in s_ancestors[v]) or (v in s_ancestors[u])
                cond2 = (u not in k_ancestors[v]) and (v not in k_ancestors[u])
                if cond1 and cond2:
                    adj[u].add(v)

        # 寻找最大团 [修正变量覆盖bug]
        max_size = 1
        nodes = list(range(1, n+1))
        for k in range(min(n, 5), 0, -1):
            for subset in combinations(nodes, k):
                valid = True
                # 修改循环变量名为u和v
                for u, v in combinations(subset, 2):
                    if v not in adj[u]:
                        valid = False
                        break
                if valid:
                    return {  # [关键修正点：保证返回原始数据]
                        'n': n,
                        'a': a_parents,  # 保持列表类型
                        'b': b_parents,  # 保持列表类型 
                        'correct_answer': k
                    }
        return {
            'n': n,
            'a': a_parents,
            'b': b_parents,
            'correct_answer': 1
        }
    
    @staticmethod
    def prompt_func(question_case):
        # 添加类型检查确保输入正确
        assert isinstance(question_case['a'], list), "Invalid a type"
        assert isinstance(question_case['b'], list), "Invalid b type"
        
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        b = ' '.join(map(str, question_case['b']))
        
        return f"""You are a programming expert. Solve the problem and put the answer within [answer] tags.

Problem:
Two rooted trees (both rooted at 1) define edge conditions:
1. In Soroush's tree: u is ancestor of v or vice versa
2. In Keshi's tree: neither is ancestor of the other

Input:
n = {n}
Soroush's parents (a_2..a_n): {a}
Keshi's parents (b_2..b_n): {b}

Output the maximum clique size. Put your final answer between [answer] and [/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

