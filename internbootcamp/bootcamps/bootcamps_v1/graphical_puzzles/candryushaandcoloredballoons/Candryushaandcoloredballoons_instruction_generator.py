import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import deque




class CandryushaandcoloredballoonsInstructionGenerator(BaseInstructionGenerator):
    """Candryushaandcoloredballoons Bootcamp指令生成器"""
    
    def __init__(self, tree_type='random', min_nodes=3, max_nodes=10):
        """
        初始化Candryushaandcoloredballoons指令生成器
        
        Args:
            tree_type: 参数描述
            min_nodes: 参数描述
            max_nodes: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.tree_type = tree_type
        self.min_nodes = max(3, min_nodes)
        self.max_nodes = max(self.min_nodes, max_nodes)
    
    def case_generator(self):
        n = random.randint(self.min_nodes, self.max_nodes)
        edges = []
        if self.tree_type == 'chain':
            edges = [(i, i+1) for i in range(1, n)]
        elif self.tree_type == 'star':
            if n < 1:
                n = 3
            center = 1
            edges = [(center, i) for i in range(2, n+1)]
        elif self.tree_type == 'random':
            edges = self.generate_random_tree(n)
        else:
            raise ValueError("Invalid tree type")
        return {"n": n, "edges": edges}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        edges = question_case['edges']
        input_lines = [f"{n}"] + [f"{x} {y}" for x, y in edges]
        input_str = '\n'.join(input_lines)
        prompt = (
            "Candryushaandcoloredballoons需要为公园的广场分配气球颜色。公园由n个广场和(n-1)条路径组成树状结构。要求若三个连续相连的广场颜色必须互不相同。请找出最小颜色数k，并给出每个广场的颜色。\n\n"
            "输入格式：\n"
            "第一行为n，接下来(n-1)行每行两个整数表示路径连接的广场。\n\n"
            "当前问题输入：\n"
            f"{input_str}\n\n"
            "请按照以下格式输出答案：\n"
            "[answer]\n"
            "k\n"
            "c1 c2 ... cn\n"
            "[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_random_tree(n):
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]
        prufer = [random.randint(1, n) for _ in range(n-2)]
        degree = [0] * (n + 1)
        for node in prufer:
            degree[node] += 1
        leaves = []
        for i in range(1, n+1):
            if degree[i] == 0:
                leaves.append(i)
        edges = []
        for node in prufer:
            if not leaves:
                break
            leaf = leaves.pop()
            edges.append((min(node, leaf), max(node, leaf)))
            degree[node] -= 1
            if degree[node] == 0:
                leaves.append(node)
            leaves = [i for i in range(1, n+1) if degree[i] == 0]
        leaves = [i for i in range(1, n+1) if degree[i] == 0]
        if len(leaves) >= 2:
            edges.append((min(leaves[0], leaves[1]), max(leaves[0], leaves[1])))
        return edges
