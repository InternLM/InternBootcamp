import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
from collections import deque




class BintersectingsubtreesInstructionGenerator(BaseInstructionGenerator):
    """Bintersectingsubtrees Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, default_n=3, max_questions=5):
        """
        初始化Bintersectingsubtrees指令生成器
        
        Args:
            max_n: 参数描述
            default_n: 参数描述
            max_questions: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.default_n = default_n
        self.max_questions = max_questions
    
    def case_generator(self):
        """增强型案例生成，保证双方子树的有效性"""
        n = random.randint(1, self.max_n)
        
        # 生成合法树结构
        edges = self._generate_spanning_tree(n)
        
        # 生成双向标号映射
        permutation = list(range(1, n+1))
        random.shuffle(permutation)
        reverse_perm = [0]*(n+1)
        for i in range(n):
            reverse_perm[permutation[i]] = i+1
        
        # 生成用户子树（保证连通）
        k1 = random.randint(1, n)
        x_list = self._find_connected_subgraph(edges, k1)
        
        # 生成李晨子树（基于映射后的树结构）
        lc_edges = [(permutation[u-1], permutation[v-1]) for u, v in edges]
        k2 = random.randint(1, n)
        y_list = self._find_connected_subgraph(lc_edges, k2)
        
        return {
            'n': n,
            'edges': edges,
            'permutation': permutation,
            'k1': k1,
            'x_list': sorted(x_list),
            'k2': k2,
            'y_list': sorted(y_list)
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        edges_str = '\n'.join(f"{u} {v}" for u, v in case['edges'])
        return f"""树结构（你的标号）：
节点数：{case['n']}
边列表：
{edges_str}

你的子树节点：{case['x_list']}
李晨的子树节点（他的标号）：{case['y_list']}

通过至多5次A/B查询确定共同节点。答案置于[answer]标签内。例：[answer]3[/answer] 或 [answer]-1[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_spanning_tree(n):
        """生成保证连通的树结构"""
        if n == 1: return []
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        root = nodes[0]
        edges = []
        connected = {root}
        for node in nodes[1:]:
            neighbor = random.choice(list(connected))
            edges.append((neighbor, node))
            connected.add(node)
        return edges

    def _find_connected_subgraph(self, edges, k):
        """DFS生成连通子图"""
        adj = [[] for _ in range(self.max_n+2)]  # 兼容大节点编号
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        start = random.choice([u for u, v in edges] + [v for u, v in edges]) if edges else 1
        visited = set()
        stack = [start]
        while stack and len(visited) < k:
            node = stack.pop()
            if node not in visited:
                visited.add(node)
                neighbors = adj[node]
                random.shuffle(neighbors)
                stack.extend(neighbors)
        return sorted(list(visited)[:k])
