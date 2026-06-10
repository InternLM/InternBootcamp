import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BweirdjourneyInstructionGenerator(BaseInstructionGenerator):
    """Bweirdjourney Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Bweirdjourney指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
    
    def case_generator(self):
        # 参数处理逻辑优化
        n = self.params.get('n', random.randint(1, 5))
        n = max(1, n)  # 保证最小城市数为1

        # 边数范围修正
        max_possible = n * (n + 1) // 2  # 包含自环的最大可能边数
        min_m = 1 if n == 1 else (n - 1)
        m = self.params.get('m', random.randint(min_m, min(max_possible, 10)))
        m = max(min_m, min(m, max_possible))  # 确保合法范围

        edges = []
        edge_set = set()

        # 处理n=1的特殊情况
        if n == 1:
            # 强制生成自环边
            edges = [(1, 1)] * m
            edge_set = set([(1,1)])
        else:
            # 生成连通图的修正逻辑
            # 生成生成树保证连通性
            nodes = list(range(1, n+1))
            random.shuffle(nodes)
            for i in range(1, n):
                u = nodes[i-1]
                v = nodes[i]
                edge = tuple(sorted((u, v)))
                edges.append((u, v))
                edge_set.add(edge)
            
            # 添加剩余边（可能包括自环）
            remaining = m - len(edges)
            while remaining > 0:
                u = random.randint(1, n)
                v = random.randint(1, n)
                if u == v:
                    if (u, v) not in edge_set:
                        edges.append((u, v))
                        edge_set.add((u, v))
                        remaining -= 1
                else:
                    edge = tuple(sorted((u, v)))
                    if edge not in edge_set:
                        edges.append((u, v))
                        edge_set.add(edge)
                        remaining -= 1

        # 正确计算结果
        expected = self.calculate_good_paths(n, m, edges)
        return {
            "n": n,
            "m": m,
            "edges": edges,
            "expected": expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges = question_case['edges']
        edges_str = '\n'.join(f"{u} {v}" for u, v in edges)
        prompt = f"""You are solving a graph theory problem about Bweirdjourney. The country has {question_case['n']} cities connected by {question_case['m']} roads. A valid path must traverse exactly {question_case['m']-2} roads twice and 2 roads once. Paths are considered different if their sets of single-use roads differ.

Road list (u v pairs):
{edges_str}

Calculate the total number of valid good paths. Provide your answer as a single integer within [answer][/answer] tags. Example: [answer]3[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_good_paths(n, m, edges):
        # 严格遵循参考代码逻辑
        special = 0
        found = [1] * n
        coupl = [[] for _ in range(n)]

        for u, v in edges:
            u0 = u - 1
            v0 = v - 1
            found[u0] = 0
            found[v0] = 0
            if u0 != v0:
                coupl[u0].append(v0)
                coupl[v0].append(u0)
            else:
                special += 1

        # 连通性检查
        root = 0
        while root < n and found[root]:
            root += 1

        if root < n:
            found[root] = 1
            bfs = [root]
            for node in bfs:
                for nei in coupl[node]:
                    if not found[nei]:
                        found[nei] = 1
                        bfs.append(nei)

        if not all(found):
            return 0

        # 计算结果
        sum_degree = sum(len(c)*(len(c)-1) for c in coupl) // 2
        sum_special = special * (special-1) // 2
        sum_mixed = special * (m - special)
        return sum_degree + sum_special + sum_mixed
