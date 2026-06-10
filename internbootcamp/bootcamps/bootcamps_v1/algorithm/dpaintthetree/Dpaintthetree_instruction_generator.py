import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from itertools import permutations
from collections import defaultdict




class DpaintthetreeInstructionGenerator(BaseInstructionGenerator):
    """Dpaintthetree Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=10, chain_prob=0.5, cost_min=1, cost_max=10):
        """
        初始化Dpaintthetree指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            chain_prob: 参数描述
            cost_min: 参数描述
            cost_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'min_n': min_n,
            'max_n': max_n,
            'chain_prob': chain_prob,
            'cost_min': cost_min,
            'cost_max': cost_max
        }
    
    def case_generator(self):
        params = self.params
        n = random.randint(params['min_n'], params['max_n'])
        
        # 生成树结构
        if random.random() < params['chain_prob'] or n < 4:
            # 生成随机链式结构
            nodes = list(range(1, n+1))
            random.shuffle(nodes)
            edges = []
            for i in range(len(nodes)-1):
                edges.append((nodes[i], nodes[i+1]))
        else:
            # 生成带有度数>2节点的树（必然无解）
            edges = []
            if n >= 4:
                edges.extend([(1,2), (1,3), (1,4)])
                current = 4
                for i in range(5, n+1):
                    edges.append((current, i))
                    current = i
        
        # 生成颜色成本
        c1 = [random.randint(params['cost_min'], params['cost_max']) for _ in range(n)]
        c2 = [random.randint(params['cost_min'], params['cost_max']) for _ in range(n)]
        c3 = [random.randint(params['cost_min'], params['cost_max']) for _ in range(n)]
        
        # 计算期望解
        expected_cost, expected_colors = self._solve_puzzle(n, c1, c2, c3, edges)
        
        return {
            'n': n,
            'c1': c1,
            'c2': c2,
            'c3': c3,
            'edges': edges,
            'expected_cost': expected_cost,
            'expected_colors': expected_colors
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges_list = '\n'.join(f"{u} {v}" for u, v in question_case['edges'])
        return f"""给定一个包含 {question_case['n']} 个顶点的树结构。需要将每个顶点染色为1/2/3，满足任何三个连续顶点的颜色不同。

颜色成本：
颜色1：{question_case['c1']}
颜色2：{question_case['c2']}
颜色3：{question_case['c3']}

边列表：
{edges_list}

请计算最小成本并给出染色方案，格式示例：
[answer]
<总成本>
<颜色序列>
[/answer]
若无解返回-1。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _solve_puzzle(n, c1, c2, c3, edges):
        # 验证树结构合法性
        adj = defaultdict(list)
        degrees = defaultdict(int)
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)
            degrees[u] += 1
            degrees[v] += 1

        if any(d > 2 for d in degrees.values()):
            return (-1, None)

        # 寻找路径端点
        start = next((node for node in adj if len(adj[node]) == 1), None)
        if not start:
            return (-1, None)

        # 动态规划求解
        min_cost = float('inf')
        best_pattern = []

        for pattern in permutations([0, 1, 2]):
            current = start
            prev = None
            total = 0
            color_seq = [0]*(n+1)
            color_idx = 0

            while True:
                color = pattern[color_idx%3]
                total += [c1[current-1], c2[current-1], c3[current-1]][color]
                color_seq[current] = color + 1

                # 移动到下一个节点
                next_nodes = [n for n in adj[current] if n != prev]
                if not next_nodes:
                    break
                prev = current
                current = next_nodes[0]
                color_idx += 1

            if total < min_cost:
                min_cost = total
                best_pattern = color_seq[1:]  # 去除0索引

        return (min_cost, best_pattern) if min_cost != float('inf') else (-1, None)
