import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class CvaleraandelectionsInstructionGenerator(BaseInstructionGenerator):
    """Cvaleraandelections Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, problem_prob=0.5):
        """
        初始化Cvaleraandelections指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            problem_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.problem_prob = problem_prob
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        nodes = list(range(1, n+1))
        random.shuffle(nodes)  # 确保各种结构的树都能生成
        
        parent_map = {}
        edges = []
        # 使用更均匀的树生成算法
        for i in range(1, n):
            parent = random.choice(nodes[:i])
            child = nodes[i]
            ti = 2 if random.random() < self.problem_prob else 1
            edges.append((parent, child, ti))
            parent_map[child] = parent
        return {
            'n': n,
            'edges': edges,
            'parent_map': parent_map  # 缓存父节点关系加速验证
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        roads = '\n'.join(f"{parent} {child} {ti}" for parent, child, ti in edges)
        return f"""The city Valera lives in has {n} districts connected by {n-1} roads forming a tree. Each road is either a problem (needs repair) or not. When candidate from district i is elected, they repair all problem roads on the path from i to district 1 (root).

Your task is to find the smallest subset of candidates such that all problem roads are repaired. If multiple solutions exist, output any.

Input:
{n}
{roads}

Output your answer as:

[answer]
k
a1 a2 ... ak
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

