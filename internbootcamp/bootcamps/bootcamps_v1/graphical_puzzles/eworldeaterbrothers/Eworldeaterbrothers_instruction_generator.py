import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
from random import randint
from random import choice
from collections import defaultdict




class EworldeaterbrothersInstructionGenerator(BaseInstructionGenerator):
    """Eworldeaterbrothers Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Eworldeaterbrothers指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 4)
        self.max_retry = params.get('max_retry', 3)  # 添加容错机制
    
    def case_generator(self):
        for _ in range(self.max_retry):
            try:
                n = self.n
                if n == 1:
                    return {'n':1, 'edges':[], 'expected':0}
                
                # 生成随机树结构（保证连通无环）
                parents = {}
                undirected_edges = []
                for i in range(2, n+1):
                    parents[i] = randint(1, i-1)
                    undirected_edges.append((parents[i], i))
                
                # 随机分配方向
                directed_edges = []
                for a, b in undirected_edges:
                    if choice([True, False]):
                        directed_edges.append((a, b))
                    else:
                        directed_edges.append((b, a))
                
                # 计算正确答案
                expected = self._calculate_min_reversals(n, directed_edges)
                return {
                    'n': n,
                    'edges': directed_edges,
                    'expected': expected
                }
            except Exception as e:
                continue
        raise RuntimeError("Case generation failed after retries")
    
    @staticmethod
    def prompt_func(question_case):
        edges = question_case['edges']
        edges_str = '\n'.join([f"{a} {b}" for a, b in edges])
        return f"""The two brothers aim to control all countries by directing roads. Find the minimal road reversals needed.

Input:
n = {question_case['n']}
Roads (directed from a to b):
{edges_str}

Output the minimal number using [answer] and [/answer]. Example: [answer]0[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_min_reversals(n, edges):
        if n <= 1:
            return 0

        # 构建双向邻接表
        h = defaultdict(list)
        edge_dict = {}
        for idx, (a, b) in enumerate(edges):
            num = idx + 1
            h[a].append({'y':b, 'v':0, 'num':num})
            h[b].append({'y':a, 'v':1, 'num':num})
            edge_dict[num] = (a, b)

        # 第一遍DFS计算层级和初始cost
        floors = [0]*(n+1)
        f = [0]*(n+1)
        stack = [(1, 0, False)]
        while stack:
            node, parent, visited = stack.pop()
            if not visited:
                floors[node] = floors[parent] + 1
                stack.append((node, parent, True))
                # 按随机顺序处理子节点（避免生成链式结构）
                children = [edge for edge in h[node] if edge['y'] != parent]
                for edge in reversed(children):
                    stack.append((edge['y'], node, False))
            else:
                f[node] = 0
                for edge in h[node]:
                    if edge['y'] != parent:
                        f[node] += f[edge['y']] + edge['v']

        min_flips = float('inf')
        processed = set()

        # 遍历所有可能的切割边
        for num in edge_dict:
            if num in processed:
                continue
            processed.add(num)

            a, b = edge_dict[num]
            # 确定父子关系
            if floors[a] > floors[b]:
                parent, child = b, a
                original_dir = 1  # 当前方向是child->parent
            else:
                parent, child = a, b
                original_dir = 0  # 当前方向是parent->child

            # 计算上半部分的最小翻转
            upper_min = f[1] - f[child] - original_dir
            stack = [(1, 0, upper_min)]
            current_min = upper_min
            while stack:
                node, father, cost = stack.pop()
                current_min = min(current_min, cost)
                for edge in h[node]:
                    if edge['y'] != father and edge['num'] != num:
                        new_cost = cost - 1 if edge['v'] else cost + 1
                        stack.append((edge['y'], node, new_cost))

            # 计算下半部分的最小翻转
            lower_min = f[child]
            stack = [(child, parent, lower_min)]
            current_lower = lower_min
            while stack:
                node, father, cost = stack.pop()
                current_lower = min(current_lower, cost)
                for edge in h[node]:
                    if edge['y'] != father and edge['num'] != num:
                        new_cost = cost - 1 if edge['v'] else cost + 1
                        stack.append((edge['y'], node, new_cost))

            min_flips = min(min_flips, current_min + current_lower)

        return min_flips if min_flips != float('inf') else 0
