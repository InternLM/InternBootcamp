import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict




class F1fallingsandeasyversionInstructionGenerator(BaseInstructionGenerator):
    """F1fallingsandeasyversion Bootcamp指令生成器"""
    
    def __init__(self, n=5, m=7, a=None):
        """
        初始化F1fallingsandeasyversion指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            a: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if a is None:
            a = [4, 1, 1, 1, 0, 3, 1]
        self.n = n
        self.m = m
        self.a = a.copy()
    
    def case_generator(self):
        n = self.n
        m = self.m
        a = self.a
        
        cols = {}
        for j in range(m):
            if a[j] == 0:
                cols[j] = set()
                continue
            # Ensure a[j] <= n
            if a[j] > n:
                a[j] = n
            sand_rows = random.sample(range(n), a[j])
            cols[j] = set(sand_rows)
        
        grid = []
        for i in range(n):
            row = []
            for j in range(m):
                row.append('#' if i in cols[j] else '.')
            grid.append(''.join(row))
        
        return {
            'grid': grid,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case['grid']
        a = question_case['a']
        n = len(grid)
        m = len(grid[0]) if n > 0 else 0
        
        prompt = (
            "You are presented with a sand puzzle. The board has {n} rows and {m} columns. "
            "Each cell is either empty ('.') or contains a sand block ('#'). When you disturb a sand block, "
            "it falls down the column, disturbing all adjacent sand blocks (up, down, left, right), which then also fall. "
            "Your goal is to determine the minimum number of sand blocks you need to disturb so that each column i has at least {a_i} sand blocks in the counter below.\n\n"
        )
        prompt += "The board is as follows:\n"
        for row in grid:
            prompt += f"{row}\n"
        prompt += (
            "The required sand blocks for each column are: {a_str}\n\n"
            "Please provide the minimum number of operations needed. Place your answer within [answer] tags."
        )
        
        # Fix the a[i] issue by using proper string formatting
        a_str = ", ".join(map(str, a))
        prompt = prompt.format(
            n=n,
            m=m,
            a_i=" (for each column i, the required sand blocks are {})".format(a_str),
            a_str=a_str
        )
        
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

