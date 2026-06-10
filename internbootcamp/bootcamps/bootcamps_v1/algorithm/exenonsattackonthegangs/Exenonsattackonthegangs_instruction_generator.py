import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class ExenonsattackonthegangsInstructionGenerator(BaseInstructionGenerator):
    """Exenonsattackonthegangs Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Exenonsattackonthegangs指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        edges = self.generate_random_tree(self.n)
        return {
            'n': self.n,
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        edge_lines = "\n".join([f"{u} {v}" for u, v in edges])
        prompt = f"""You are Xenon, a cybersecurity expert. A network of {n} gangs forms a tree structure. Each edge must be assigned a distinct integer from 0 to {n-2}. The password layers S is the sum of mex(u, v) for all pairs u < v, where mex is the minimum non-negative integer not present on the path between u and v. Find the maximum possible S.

Input:
{n}
{edge_lines}

Output the maximum S. Put your final answer within [answer] and [/answer], like [answer]5[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_random_tree(n):
        if n == 1:
            return []
        edges = []
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        for i in range(1, n):
            u = nodes[i]
            v = nodes[random.randint(0, i-1)]
            edges.append((min(u, v), max(u, v)))
        return edges
