import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque
import re




class BminimumdiametertreeInstructionGenerator(BaseInstructionGenerator):
    """Bminimumdiametertree Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, s_min=1, s_max=10**9):
        """
        初始化Bminimumdiametertree指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            s_min: 参数描述
            s_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.s_min = s_min
        self.s_max = s_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        s = random.randint(self.s_min, self.s_max)
        
        # 使用BFS生成更平衡的树结构
        edges = []
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        
        root = nodes[0]
        available = deque([root])
        used = {root}
        
        for node in nodes[1:]:
            parent = random.choice(available)
            edges.append((parent, node))
            used.add(node)
            available.append(node)
            
            # 保持连接数多样性
            if len(available) > 3 and random.random() < 0.5:
                available.popleft()

        # 正确计算叶节点数
        adj = defaultdict(set)
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)
        
        leaf_count = sum(1 for node in adj if len(adj[node]) == 1)
        
        return {
            'n': n,
            's': s,
            'edges': edges,
            'leaf_count': leaf_count
        }
    
    @staticmethod
    def prompt_func(question_case):
        edges_str = "\n".join(f"{a} {b}" for a, b in question_case['edges'])
        return f"""Given a tree with {question_case['n']} nodes and total edge weight sum {question_case['s']}. 
Assign non-negative weights to edges such that:
1. Sum of weights equals {question_case['s']}
2. The diameter (max path weight between any two nodes) is minimized

Edges:
{edges_str}

Calculate the minimal possible diameter. Format your answer with 12+ decimal places within [answer] tags like:
[answer]3.141592653589[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

