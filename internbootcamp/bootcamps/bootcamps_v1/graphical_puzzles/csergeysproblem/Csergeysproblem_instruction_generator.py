import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class CsergeysproblemInstructionGenerator(BaseInstructionGenerator):
    """Csergeysproblem Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Csergeysproblem指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 5)
        self.m = params.get('m', 4)
    
    def case_generator(self):
        n = self.n
        m = self.m
        edges = []
        for _ in range(m):
            a = random.randint(1, n)
            b = random.randint(1, n)
            while a == b:
                b = random.randint(1, n)
            edges.append((a, b))
        return {
            'n': n,
            'm': m,
            'edges': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        edges = question_case['edges']
        input_lines = [f"{n} {m}"] + [f"{a} {b}" for a, b in edges]
        input_example = '\n'.join(input_lines)
        prompt = f"""Sergey在他的五岁生日时得到了一个有向图，他需要找到满足特定条件的顶点集合Q。具体规则如下：

1. Q中的任意两个顶点之间不能有直接相连的边（即不存在边x→y或y→x，其中x和y都属于Q）。
2. 所有不在Q中的顶点z必须满足：至少存在一个顶点x属于Q，使得z可以通过x的一步或两步到达（即存在x→z的边，或存在中间顶点u，使得x→u→z的路径）。

你的任务是，给定一个有向图，找到这样的集合Q。输出可以是任意有效解，无需最小化集合大小。

输入格式：
第一行包含两个整数n和m（顶点数和边数）。
接下来的m行每行两个整数a_i和b_i，表示一条有向边。

输出格式：
第一行输出k（集合Q的顶点数量），第二行输出k个不同的顶点编号，按任意顺序排列，用空格分隔。

例如，输入：
5 4
1 2
2 3
2 4
2 5
有效输出：
4
1 3 4 5 

现在，给定以下输入，请找出符合条件的顶点集合Q，并将答案按格式包含在[answer]和[/answer]标签中：

输入：
{input_example}

请将最终答案放在[answer]标签内。例如：
[answer]
3
1 2 3
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

