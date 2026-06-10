import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class EfibtreeInstructionGenerator(BaseInstructionGenerator):
    """Efibtree Bootcamp指令生成器"""
    
    def __init__(self, yes_prob=0.5, case_type=None, max_n=200000):
        """
        初始化Efibtree指令生成器
        
        Args:
            yes_prob: 参数描述
            case_type: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.yes_prob = yes_prob
        self.case_type = case_type
        self.max_n = max_n

        # 预计算斐波那契数列
        self.fib = [1, 1]
        while True:
            next_f = self.fib[-1] + self.fib[-2]
            if next_f > max_n:
                break
            self.fib.append(next_f)
        self.fib_set = set(self.fib)
    
    def case_generator(self):
        # 类型决策逻辑
        if self.case_type is not None:
            generate_yes = (self.case_type == 'YES')
        else:
            generate_yes = random.random() < self.yes_prob
        
        if generate_yes:
            valid_ks = [k for k, f in enumerate(self.fib) if 1 <= f <= self.max_n and k >= 0]
            if not valid_ks:
                valid_ks = [0, 1]
            k = random.choice(valid_ks)
            n = self.fib[k]
            
            # 特殊处理小案例
            if k <= 1:
                return {'n': n, 'edges': [], 'expected': 'YES'}
            
            tree = self._build_fib_tree(k)
            return {
                'n': n,
                'edges': tree['edges'],
                'expected': 'YES'
            }
        else:
            # 生成两种NO案例类型
            if random.random() < 0.5:
                # 类型A：n非斐波那契数
                while True:
                    n = random.randint(1, self.max_n)
                    if n not in self.fib_set:
                        break
                # 生成链式结构
                edges = [[i, i+1] for i in range(1, n)]
                return {'n': n, 'edges': edges, 'expected': 'NO'}
            else:
                # 类型B：斐波那契数但结构非法
                valid_ks = [k for k, f in enumerate(self.fib) if f >=5 and f <= self.max_n]
                k = random.choice(valid_ks)
                n = self.fib[k]
                # 生成星型结构
                edges = [[1, i] for i in range(2, n+1)]
                return {'n': n, 'edges': edges, 'expected': 'NO'}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        edges = question_case['edges']
        edge_list = '\n'.join(f"{u} {v}" for u, v in edges)
        return f"""判断给定的树是否为Fib-tree。规则如下：
1. 顶点数必须是斐波那契数（F_0=1, F_1=1, F_n=F_{{n-1}}+F_{{n-2}}）
2. 单个顶点或可通过移除一条边分割为两个Fib-tree

输入：
{n}
{edge_list}

请将答案（YES/NO）放在[answer]标签内，例如：[answer]YES[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _build_fib_tree(self, k):
        """动态构建符合Fib-tree的随机结构"""
        if k == 0 or k == 1:
            return {'nodes': [1], 'edges': []}

        # 随机选择分割比例（允许不同分割方向）
        left_k = k-1
        right_k = k-2
        if random.random() < 0.5 and k >= 3:
            left_k, right_k = right_k, left_k

        left = self._build_fib_tree(left_k)
        right = self._build_fib_tree(right_k)

        # 动态计算节点偏移
        max_left = max(left['nodes'])
        right_nodes = [n + max_left for n in right['nodes']]
        right_edges = [[u+max_left, v+max_left] for u, v in right['edges']]

        # 随机选择连接点
        connect_point = random.choice(left['nodes'])
        new_node = max_left + 1 if not right['nodes'] else right_nodes[0]

        return {
            'nodes': left['nodes'] + right_nodes,
            'edges': left['edges'] + right_edges + [[connect_point, new_node]]
        }
