import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from math import gcd
from collections import deque




class CcycliccoloringInstructionGenerator(BaseInstructionGenerator):
    """Ccycliccoloring Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, min_k=1, max_k=5):
        """
        初始化Ccycliccoloring指令生成器
        
        Args:
            max_n: 参数描述
            min_k: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.min_k = min_k
        self.max_k = max_k
    
    def case_generator(self):
        # 核心改进：确保生成合法k的测试用例
        while True:
            try:
                n = random.randint(2, self.max_n)
                k = random.randint(self.min_k, min(self.max_k, n))
                
                # 生成合法颜色分配
                colors = {}
                nodes = list(range(n))
                random.shuffle(nodes)
                
                # 创建至少一个长度为k的环确保解至少为k
                cycle = nodes[:k]
                for i, node in enumerate(cycle):
                    colors[node] = i
                
                # 分配剩余节点颜色
                for node in nodes[k:]:
                    colors[node] = random.randint(0, k-1)
                
                # 生成合法边集合
                edges = []
                # 强制生成环
                for i in range(k):
                    u = cycle[i]
                    v = cycle[(i+1) % k]
                    edges.append((u+1, v+1))  # 1-based
                
                # 添加合法随机边
                additional_edges = []
                for _ in range(random.randint(0, 3)):  # 控制边的数量
                    u = random.choice(nodes)
                    valid_color = (colors[u] + 1) % k
                    valid_nodes = [node for node in nodes if colors[node] == valid_color]
                    if valid_nodes:
                        v = random.choice(valid_nodes)
                        additional_edges.append((u+1, v+1))
                
                # 合并边并检查自环
                edges += additional_edges
                if any(u == v for u, v in edges):
                    return {'n': n, 'm': len(edges), 'edges': edges}
                
                # 最终校验
                test_case = {'n': n, 'edges': edges}
                if self._verify_correction(k, test_case):
                    return {'n': n, 'm': len(edges), 'edges': edges}
            except:
                continue
    
    @staticmethod
    def prompt_func(question_case):
        edges_str = '\n'.join(f"{u} {v}" for u, v in question_case['edges'])
        return (
            f"给定一个有向图，{question_case['n']}个顶点，{question_case['m']}条边。"
            f"找到最大的k使得存在颜色1~k的着色方案，满足每条边u→v中v的颜色是u颜色的下一个（循环顺序）。\n"
            f"输入：\n{question_case['n']} {question_case['m']}\n{edges_str}\n"
            f"答案请写在[answer]和[/answer]之间。"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

