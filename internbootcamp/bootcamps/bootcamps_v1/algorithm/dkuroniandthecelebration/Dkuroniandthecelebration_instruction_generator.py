import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DkuroniandthecelebrationInstructionGenerator(BaseInstructionGenerator):
    """Dkuroniandthecelebration Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dkuroniandthecelebration指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化训练场类，设置默认参数以保存谜题相关参数。
        """
        self.n = params.get('n', random.randint(2, 1000))
        self.r = params.get('r', random.randint(1, self.n))
        self.edges = []
    
    def case_generator(self):
        """
        生成谜题实例，返回一个包含树结构和根节点的字典。
        """
        # 生成一个随机树
        self.n = random.randint(2, 1000)
        self.r = random.randint(1, self.n)
        self.edges = self.generate_tree(self.n, self.r)
        return {
            'n': self.n,
            'edges': self.edges.copy(),
            'root': self.r
        }
    
    @staticmethod
    def prompt_func(question_case):
        """
        将问题实例转换为文本形式的问题描述。
        """
        n = question_case['n']
        edges = question_case['edges']
        edge_strings = [f"{x} {y}" for x, y in edges]
        edge_list = "\n".join(edge_strings)
        prompt = (
            f"给定一棵包含{n}个节点的树，边如下所示：\n\n{edge_list}\n\n"
            "你需要通过查询两个节点的LCA来找出这棵树的根节点r。"
            f"每次查询的次数不能超过⌊{n}/2⌋次。\n"
            "找到根节点后，请输出它，放在[answer]标签中。例如：[answer]4[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_tree(self, n, root):
        """
        生成一棵树的边列表，确保根节点为root。
        """
        edges = []
        nodes = list(range(1, n + 1))
        nodes.remove(root)
        # 使用随机方式生成树，确保根节点连接到所有子节点
        from collections import deque
        visited = set()
        visited.add(root)
        queue = deque()
        queue.append(root)
        while nodes and queue:
            u = queue.popleft()
            if nodes:
                v = random.choice(nodes)
                edges.append((u, v))
                visited.add(v)
                nodes.remove(v)
                queue.append(v)
        return edges
