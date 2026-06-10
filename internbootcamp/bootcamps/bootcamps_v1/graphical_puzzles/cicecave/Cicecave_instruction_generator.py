import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
from random import randint
from random import random




class CicecaveInstructionGenerator(BaseInstructionGenerator):
    """Cicecave Bootcamp指令生成器"""
    
    def __init__(self, n=5, m=5, p=0.3):
        """
        初始化Cicecave指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            p: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化冰洞谜题训练场参数。
        :param n: 网格行数，默认为5
        :param m: 网格列数，默认为5
        :param p: 其他单元格为'X'的概率，默认为0.3
        """
        self.n = n
        self.m = m
        self.p = p
    
    def case_generator(self):
        """
        生成冰洞谜题的实例。确保起点为'X'，其他单元格随机生成。
        返回包含网格大小、网格状态、起点和终点的字典。
        """
        # 初始化网格
        grid = [['.' for _ in range(self.m)] for _ in range(self.n)]
        # 随机选择起点，并确保为'X'
        r1 = randint(1, self.n)
        c1 = randint(1, self.m)
        grid[r1-1][c1-1] = 'X'
        
        # 随机填充其他单元格
        for i in range(self.n):
            for j in range(self.m):
                if (i, j) == (r1-1, c1-1):
                    continue
                if random() < self.p:
                    grid[i][j] = 'X'
        
        # 转换为字符串列表便于存储
        grid_str = [''.join(row) for row in grid]
        
        # 随机选择终点
        r2 = randint(1, self.n)
        c2 = randint(1, self.m)
        
        return {
            'n': self.n,
            'm': self.m,
            'grid': grid_str,
            'start': (r1, c1),
            'end': (r2, c2)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """将谜题实例转换为文本描述的问题，包含规则和具体实例。"""
        n = question_case['n']
        m = question_case['m']
        grid = '\n'.join(question_case['grid'])
        r1, c1 = question_case['start']
        r2, c2 = question_case['end']
        return f"""你正在玩一个电脑游戏。你的角色站在一个多层冰洞的某一层。要前进，你需要下降到更下一层，唯一的方法是掉落通过冰块。

当前层的洞穴是一个由{n}行{m}列组成的矩形网格。每个单元格由完整冰块（.）或裂缝冰块（X）组成。从每个单元格，你可以移动到相邻的四个方向（上下左右）。移动到裂缝冰块（X）时，你会掉下去。移动到完整冰块（.）时，该冰块会变成裂缝冰块（X）。

你的任务是判断：从起始位置（{r1}, {c1}）出发，能否找到一条路径，使得在移动到目标位置（{r2}, {c2}）的单元格时，该单元格为裂缝冰块（X），从而掉落下去。

初始时，起始位置的冰块已经破裂（X）。其他单元格的状态如下：

{grid}

请判断是否可以达成目标。如果可能，输出“YES”；否则输出“NO”。请将你的答案放置在[answer]标签内，例如：[answer]YES[/answer]或[answer]NO[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

