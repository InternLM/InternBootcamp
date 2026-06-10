import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque
import math




class EgameontreeInstructionGenerator(BaseInstructionGenerator):
    """Egameontree Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10):
        """
        初始化Egameontree指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(min_n, 1)
        self.max_n = max(max_n, self.min_n)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        
        if n == 1:
            return {'n': 1, 'edges': [], 'expected': 1.0}
        
        # 生成随机树的优化算法（保证连通性）
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        root = nodes[0]
        parent_map = {}
        edges = []
        for i in range(1, len(nodes)):
            parent = random.choice(nodes[:i])
            edges.append((parent, nodes[i]))
            parent_map[nodes[i]] = parent
        
        # 确保生成的是有效树结构
        expected = self._compute_expected(n, edges)
        return {
            'n': n,
            'edges': sorted([(min(a,b), max(a,b)) for a,b in edges]),  # 标准化边格式
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        edges = question_case['edges']
        
        # 处理输入格式的换行符问题
        input_lines = [str(n)]
        if n > 1:
            input_lines += [f"{a} {b}" for a, b in edges]
        
        # 避免在f-string中直接使用换行符表达式
        input_str = '\n'.join(input_lines)
        example = ""
        if n == 2 and edges == [(1,2)]:
            example = "\n示例输入输出与第一个官方样例一致"
        
        return f"""Momiji有一个根树，包含{n}个节点，根节点是1。每一步随机选择剩余节点并删除其子树，求期望步骤数。

输入数据：
{input_str}

输出要求：
1. 结果保留至少12位小数
2. 将最终答案包裹在[answer]标签内
3. 示例格式：[answer]1.500000000000[/answer]{example}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _compute_expected(self, n, edges):
        if n == 1:
            return 1.0

        # 构建邻接表并计算深度
        adj = [[] for _ in range(n+1)]  # 使用1-based索引
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)

        depth = [0]*(n+1)
        depth[1] = 1  # 根节点为1
        q = deque([1])
        while q:
            u = q.popleft()
            for v in adj[u]:
                if depth[v] == 0 and v != 1:
                    depth[v] = depth[u] + 1
                    q.append(v)
        return sum(1.0/d for d in depth[1:n+1])  # 只取有效节点
