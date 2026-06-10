import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class CnewyearanddominoInstructionGenerator(BaseInstructionGenerator):
    """Cnewyearanddomino Bootcamp指令生成器"""
    
    def __init__(self, h=5, w=5, p=0.7, max_queries=5):
        """
        初始化Cnewyearanddomino指令生成器
        
        Args:
            h: 参数描述
            w: 参数描述
            p: 参数描述
            max_queries: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.h = h
        self.w = w
        self.p = p  # Probability of empty cell
        self.max_queries = max_queries  # Number of queries per case
    
    def case_generator(self):
        # Generate valid grid
        while True:
            grid = [['.' if random.random() < self.p else '#' for _ in range(self.w)] for _ in range(self.h)]
            if sum(cell == '.' for row in grid for cell in row) >= 2:  # Ensure at least 2 empty cells
                break

        # Generate multiple queries
        queries = []
        correct_answers = []
        for _ in range(random.randint(1, self.max_queries)):
            r1 = random.randint(1, self.h)
            r2 = random.randint(r1, self.h)
            c1 = random.randint(1, self.w)
            c2 = random.randint(c1, self.w)
            query = (r1, c1, r2, c2)
            answer = self.compute_answer(grid, query)
            queries.append(query)
            correct_answers.append(answer)

        return {
            'h': self.h,
            'w': self.w,
            'grid': [''.join(row) for row in grid],
            'queries': queries,
            'correct_answers': correct_answers
        }
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case['grid']
        queries = question_case['queries']
        prompt = f"""Limak needs help counting domino placements in a {len(grid)}x{len(grid[0])} grid:

Grid (rows 1-{len(grid)}):
""" + '\n'.join(f"Row {i+1}: {row}" for i, row in enumerate(grid)) + """

Answer these queries (format as space-separated numbers in [answer] tags):
"""
        for i, (r1, c1, r2, c2) in enumerate(queries, 1):
            prompt += f"\nQuery {i}: Rectangle from ({r1}, {c1}) to ({r2}, {c2})"
        
        prompt += "\n\nPlace your final answer between [answer] and [/answer], e.g.: [answer]1 4 0 5[/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def compute_answer(self, grid, query):
        h, w = len(grid), len(grid[0])
        r1, c1, r2, c2 = query

        # Build prefix sums for vertical dominoes
        d1 = defaultdict(int)
        for i in range(h+1):
            for j in range(w+1):
                if i <= 1 or j == 0:
                    d1[(i, j)] = 0
                else:
                    term = 1 if (i >= 2 and 
                                grid[i-1][j-1] == '.' and 
                                grid[i-2][j-1] == '.') else 0
                    d1[(i, j)] = d1[(i-1, j)] + d1[(i, j-1)] - d1[(i-1, j-1)] + term

        # Build prefix sums for horizontal dominoes
        d2 = defaultdict(int)
        for i in range(h+1):
            for j in range(w+1):
                if j <= 1 or i == 0:
                    d2[(i, j)] = 0
                else:
                    term = 1 if (j >= 2 and 
                                grid[i-1][j-1] == '.' and 
                                grid[i-1][j-2] == '.') else 0
                    d2[(i, j)] = d2[(i-1, j)] + d2[(i, j-1)] - d2[(i-1, j-1)] + term

        # Calculate sum for vertical dominoes
        def sum_vertical(r1, c1, r2, c2):
            a = d1.get((r1-1, c1-1), 0)
            b = d1.get((r1-1, c2), 0)
            c_val = d1.get((r2, c1-1), 0)
            d_val = d1.get((r2, c2), 0)
            return d_val - b - c_val + a

        # Calculate sum for horizontal dominoes
        def sum_horizontal(r1, c1, r2, c2):
            a = d2.get((r1-1, c1-1), 0)
            b = d2.get((r1-1, c2), 0)
            c_val = d2.get((r2, c1-1), 0)
            d_val = d2.get((r2, c2), 0)
            return d_val - b - c_val + a

        total = 0
        # Vertical dominoes (need at least 2 rows)
        if r2 >= r1 + 1:
            total += sum_vertical(r1+1, c1, r2, c2)
        # Horizontal dominoes (need at least 2 columns)
        if c2 >= c1 + 1:
            total += sum_horizontal(r1, c1+1, r2, c2)

        return total
