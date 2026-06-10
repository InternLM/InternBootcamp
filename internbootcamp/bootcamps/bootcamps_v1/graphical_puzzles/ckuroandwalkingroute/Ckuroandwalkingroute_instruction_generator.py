import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict




class CkuroandwalkingrouteInstructionGenerator(BaseInstructionGenerator):
    """Ckuroandwalkingroute Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, default_n=None, x=None, y=None):
        """
        初始化Ckuroandwalkingroute指令生成器
        
        Args:
            max_n: 参数描述
            default_n: 参数描述
            x: 参数描述
            y: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数，设置生成案例的最大n值、默认n值以及固定的x/y（可选）
        """
        self.params = {
            'max_n': max_n,
            'default_n': default_n,
            'x': x,
            'y': y
        }
    
    def case_generator(self):
        """
        生成符合题目要求的树结构案例，包含n、x、y、边列表及正确答案
        """
        n = self.params['default_n'] if self.params['default_n'] is not None else random.randint(2, self.params['max_n'])
        edges = []
        
        if n > 1:
            parents = {}
            # 生成随机树结构
            for i in range(2, n+1):
                p = random.randint(1, i-1)
                parents[i] = p
                edges.append((p, i))
        
        adj = defaultdict(list)
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)
        
        # 确定x和y的值，确保x != y
        x = self.params['x'] if self.params['x'] is not None else random.randint(1, n)
        y = self.params['y'] if self.params['y'] is not None else random.choice([i for i in range(1, n+1) if i != x])
        while x == y:  # 确保x和y不同
            y = random.randint(1, n)
        
        # 计算正确答案
        num_f = self._compute_under_except(adj, x, y)
        num_b = self._compute_under_except(adj, y, x)
        correct = n * (n - 1) - num_f * num_b
        
        return {
            'n': n,
            'x': x,
            'y': y,
            'edges': edges,
            'correct_answer': correct
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将案例转换为自然语言问题描述，包含输入格式和答案格式要求
        """
        n = question_case['n']
        x = question_case['x']
        y = question_case['y']
        edges = question_case['edges']
        
        input_lines = [f"{a} {b}" for a, b in edges]
        input_str = f"{n} {x} {y}\n" + "\n".join(input_lines)
        
        return f"""Ckuroandwalkingroute需要选择一条跑步路线，该路线不能先后经过Flowrisa（城镇{x}）和Beetopia（城镇{y}）。Uberland有{n}个城镇，通过以下道路连接：

{input_str}

请计算有效的(u, v)路径对的数量（u≠v），其中路径不会先经过{x}再经过{y}。答案应为整数，放在[answer]标签内。例如：[answer]5[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _compute_under_except(self, adj, start, end):
        """
        计算underExcept值：从start出发不经过通向end路径的子树大小
        """
        if start == end:
            return 0

        path = self._find_path(adj, start, end)
        if not path:
            return 0

        next_node = path[1] if len(path) > 1 else None
        total = 1  # 包含start自己

        for neighbor in adj[start]:
            if neighbor == next_node:
                continue

            # 计算该邻接点子树的节点数
            count = 0
            visited = {start}
            stack = [neighbor]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                count += 1
                for v in adj[node]:
                    if v not in visited:
                        stack.append(v)
            total += count

        return total

    def _find_path(self, adj, start, end):
        """
        使用BFS找到start到end的路径
        """
        parent = {}
        queue = deque([start])
        parent[start] = None

        while queue:
            u = queue.popleft()
            if u == end:
                break
            for v in adj[u]:
                if v not in parent and v != parent.get(u):
                    parent[v] = u
                    queue.append(v)

        if end not in parent:
            return []

        # 重建路径
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = parent[current]
        return path[::-1]
