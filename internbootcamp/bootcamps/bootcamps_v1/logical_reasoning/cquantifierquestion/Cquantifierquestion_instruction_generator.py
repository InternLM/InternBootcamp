import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class CquantifierquestionInstructionGenerator(BaseInstructionGenerator):
    """Cquantifierquestion Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=5, m_min=1, m_max=5):
        """
        初始化Cquantifierquestion指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_min = m_min
        self.m_max = m_max
    
    def case_generator(self):
        # 生成DAG的边
        n = random.randint(self.n_min, self.n_max)
        # 生成拓扑序
        top_order = list(range(1, n+1))
        random.shuffle(top_order)
        
        # 生成所有可能的边（仅从前到后）
        possible_edges = []
        for i in range(len(top_order)):
            for j in range(i+1, len(top_order)):
                possible_edges.append((top_order[i], top_order[j]))
        
        # 确定边的数量
        max_valid_edges = len(possible_edges)
        m = random.randint(max(self.m_min, 1), min(self.m_max, max_valid_edges))
        edges = random.sample(possible_edges, m) if possible_edges else []
        
        return {
            'n': n,
            'm': len(edges),
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges = question_case['edges']
        edges_str = '\n'.join(f"{j} {k}" for j, k in edges)
        return f"""请为以下逻辑问题分配量词（A/E）使表达式为真且全称最多：
变量数：{question_case['n']}，不等式数：{question_case['m']}
不等式列表：
{edges_str}
答案格式：[answer]...[/answer]，若无解输出-1""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def reference_solution(cls, identity):
        # 完全复制参考代码逻辑
        def toposort(graph):
            n = len(graph)
            res = []
            found = [0]*n

            for i in range(n):
                if found[i]:
                    continue
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node < 0:
                        res.append(~node)
                    elif not found[node]:
                        found[node] = 1
                        stack.append(~node)
                        for nei in graph[node]:
                            if not found[nei]:
                                stack.append(nei)

            # Check cycle
            found = [0]*n
            for node in res:
                if found[node]:
                    return None
                stack = [node]
                found[node] = 1
                while stack:
                    current = stack.pop()
                    for nei in graph[current]:
                        if found[nei]:
                            return None
                        if not found[nei]:
                            found[nei] = 1
                            stack.append(nei)
            return res[::-1]

        n = identity['n']
        edges = identity['edges']
        coupl1 = [[] for _ in range(n)]
        coupl2 = [[] for _ in range(n)]
        for j, k in edges:
            u = j - 1
            v = k - 1
            coupl1[u].append(v)
            coupl2[v].append(u)

        order = toposort(coupl1)
        if order is None:
            return -1

        seen1 = list(range(n))
        seen2 = list(range(n))

        for node in order:
            for nei in coupl1[node]:
                if seen1[nei] > seen1[node]:
                    seen1[nei] = seen1[node]

        for node in reversed(order):
            for nei in coupl2[node]:
                if seen2[nei] > seen2[node]:
                    seen2[nei] = seen2[node]

        seen = [(seen1[i] == i and seen2[i] == i) for i in range(n)]
        count = sum(seen)
        if count == 0:
            return -1
        quant = ''.join('A' if c else 'E' for c in seen)
        return (count, quant)
