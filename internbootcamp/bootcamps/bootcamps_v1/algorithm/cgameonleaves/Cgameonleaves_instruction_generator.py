import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class CgameonleavesInstructionGenerator(BaseInstructionGenerator):
    """Cgameonleaves Bootcamp指令生成器"""
    
    def __init__(self, min_nodes=1, max_nodes=1000, **kwargs):
        """
        初始化Cgameonleaves指令生成器
        
        Args:
            min_nodes: 参数描述
            max_nodes: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
    
    def case_generator(self):
        n = random.randint(self.min_nodes, self.max_nodes)
        edges = []
        if n > 1:
            nodes = set(range(1, n+1))
            connected = {random.choice(list(nodes))}
            while len(connected) < n:
                u = random.choice(list(nodes - connected))
                v = random.choice(list(connected))
                edges.append((u, v))
                connected.add(u)
        x = random.randint(1, n)
        return {
            'n': n,
            'x': x,
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        x = question_case['x']
        edges = question_case['edges']
        input_lines = [f"1\n{n} {x}"] + [f"{u} {v}" for u, v in edges]
        
        return (
            "Determine the winner of the tree node removal game between Ayush and Ashish.\n\n"
            "Game Rules:\n"
            "1. Players alternate turns removing leaf nodes (degree ≤ 1)\n"
            "2. The player who removes node x wins\n"
            "3. Ayush moves first\n\n"
            f"Test Case Input (n={n}, x={x}):\n" + 
            '\n'.join(input_lines) +
            "\n\nAnswer format: [answer]Winner[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

