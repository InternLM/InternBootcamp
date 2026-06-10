import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Frectanglepainting1InstructionGenerator(BaseInstructionGenerator):
    """Frectanglepainting1 Bootcamp指令生成器"""
    
    def __init__(self, n_min=3, n_max=8, black_prob=0.4):
        """
        初始化Frectanglepainting1指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            black_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(1, n_min)
        self.n_max = min(50, n_max)  # 根据题目约束调整范围
        self.black_prob = black_prob
    
    def case_generator(self):
        while True:
            n = random.randint(self.n_min, self.n_max)
            grid = [
                ['#' if random.random() < self.black_prob else '.' 
                 for _ in range(n)]
                for _ in range(n)
            ]
            
            # 确保至少有一个黑格或全白
            black_count = sum(row.count('#') for row in grid)
            if black_count == 0:
                correct_answer = 0
                break
                
            try:
                correct_answer = self.calculate_min_cost([row[:] for row in grid])
                break
            except RecursionError:
                continue  # 处理极大网格时的递归深度问题

        return {
            'n': n,
            'grid': [''.join(row) for row in grid],
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])] + question_case['grid']
        problem_instance = '\n'.join(input_lines)
        return f"""你正在解决一个网格涂白优化问题。给定一个n×n网格，每次可选择任意矩形区域涂白，费用为矩形高度和宽度的较大值。请计算将所有黑色格子涂白的最小总费用。

输入格式：
第一行为整数n
随后n行，每行n个字符（.表示白色，#表示黑色）

当前问题：
{problem_instance}

请将最终答案放在[answer]标签内，例如：[answer]5[/answer]。答案应为整数。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_min_cost(grid):
        n = len(grid)
        memo = {}

        def solve(r1, c1, r2, c2):
            if r1 > r2 or c1 > c2:
                return 0
            key = (r1, c1, r2, c2)
            if key in memo:
                return memo[key]

            # 优化全白判断
            has_black = False
            for i in range(r1, r2+1):
                if '#' in grid[i][c1:c2+1]:
                    has_black = True
                    break
            if not has_black:
                memo[key] = 0
                return 0

            min_cost = max(r2-r1+1, c2-c1+1)

            # 水平分割优化
            for i in range(r1, r2):
                cost = solve(r1, c1, i, c2) + solve(i+1, c1, r2, c2)
                if cost < min_cost:
                    min_cost = cost
                    if min_cost == 1:  # 提前终止
                        break

            # 垂直分割优化
            for j in range(c1, c2):
                cost = solve(r1, c1, r2, j) + solve(r1, j+1, r2, c2)
                if cost < min_cost:
                    min_cost = cost
                    if min_cost == 1:
                        break

            memo[key] = min_cost
            return min_cost

        return solve(0, 0, n-1, n-1)
