import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re
from typing import Dict
from typing import Any
from typing import Optional
from collections import defaultdict
from collections import deque




class EjeremybearimyInstructionGenerator(BaseInstructionGenerator):
    """Ejeremybearimy Bootcamp指令生成器"""
    
    def __init__(self, k: int = 3):
        """
        初始化Ejeremybearimy指令生成器
        
        Args:
            k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场参数
        :param k: 灵魂伴侣对数
        """
        self.k = k
    
    def case_generator(self) -> Dict[str, Any]:
        """
        生成谜题实例
        :return: 包含树结构和答案的字典
        """
        n = 2 * self.k
        adj = [[] for _ in range(n)]
        edges = []
        root = 0
        visited = [False] * n
        q = deque([root])
        visited[root] = True

        while len(edges) < n - 1:
            u = random.choice(q)
            v = random.randint(0, n - 1)
            if not visited[v]:
                visited[v] = True
                adj[u].append(v)
                adj[v].append(u)
                q.append(v)
                weight = random.randint(1, 100)
                edges.append((u + 1, v + 1, weight))
            else:
                found = False
                while not found:
                    v = random.randint(0, n - 1)
                    if not visited[v] and v != u:
                        visited[v] = True
                        adj[u].append(v)
                        adj[v].append(u)
                        q.append(v)
                        weight = random.randint(1, 100)
                        edges.append((u + 1, v + 1, weight))
                        found = True

        edge_contributions = []

        def dfs(u, parent):
            size = 1
            for v in adj[u]:
                if v != parent:
                    child_size = dfs(v, u)
                    size += child_size
                    # Find the corresponding edge weight
                    for a, b, w in edges:
                        if (a == u + 1 and b == v + 1) or (a == v + 1 and b == u + 1):
                            edge_contributions.append((w, child_size))
                            break
            return size

        dfs(root, -1)

        G = 0
        B = 0
        for weight, cnt in edge_contributions:
            G += weight * (cnt % 2)
            B += weight * cnt

        case = {
            'k': self.k,
            'edges': edges,
            'G': G,
            'B': B
        }
        return case
    
    @staticmethod
    def prompt_func(question_case: Dict[str, Any]) -> str:
        """
        将问题实例转换为提示文本
        :param question_case: 生成的问题实例
        :return: 提示字符串
        """
        k = question_case['k']
        edges = question_case['edges']
        edge_list = "\n".join([f"House {a} connected to house {b} (time {t})" for a, b, t in edges])
        prompt = (
            "You are a soulmate assignment expert. Given a neighborhood of {total_houses} houses connected as a tree, "
            "you need to assign {pairs} pairs of soulmates to minimize and maximize the total travel time between each pair.\n"
            "The tree structure is:\n{edges}\n"
            "Compute two values:\n"
            "- G: Minimum possible total travel time\n"
            "- B: Maximum possible total travel time\n"
            "Please output your answer in the format:\n"
            "[answer]\nG = {G}, B = {B}\n[/answer]"
        ).format(
            total_houses=2 * k,
            pairs=k,
            edges=edge_list,
            G='G',
            B='B'
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

