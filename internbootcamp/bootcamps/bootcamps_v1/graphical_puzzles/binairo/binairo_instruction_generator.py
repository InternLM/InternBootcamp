import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BinairoInstructionGenerator(BaseInstructionGenerator):
    """Binairo Bootcamp指令生成器"""
    
    def __init__(self, size=6, clue_density=0.5):
        """
        初始化Binairo指令生成器
        
        Args:
            size: 参数描述
            clue_density: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if size % 2 != 0:
            raise ValueError("Size must be even for Binairo puzzle.")
        self.size = size
        self.clue_density = clue_density
    
    def case_generator(self):
        solution = self.generate_solution()
        puzzle = [
            [
                cell if random.random() < self.clue_density else None 
                for cell in row
            ]
            for row in solution
        ]
        return {'puzzle': puzzle, 'solution': solution}
    
    @staticmethod
    def prompt_func(question_case):
        puzzle = question_case['puzzle']
        size = len(puzzle)
        rows = []
        for i, row in enumerate(puzzle, 1):
            cells = ['_' if c is None else str(c) for c in row]
            rows.append(f"Row {i}: {' '.join(cells)}")
        return f"""Solve this Binairo puzzle (size {size}x{size}):

Rules:
1. Equal 0s/1s in each row/column
2. No three consecutive identical digits
3. All rows/columns must be unique
4. Exactly one valid solution

Puzzle:
{chr(10).join(rows)}

Place your final answer between [answer] and [/answer] tags as:

[answer]
1 0 1 0
0 1 0 1
...[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_solution(self):
        n = self.size
        possible_rows = self.generate_all_possible_rows(n)
        random.shuffle(possible_rows)

        for _ in range(1000):
            try:
                selected = random.sample(possible_rows, n)
            except ValueError:
                continue

            if len({tuple(r) for r in selected}) != n:
                continue

            if self.check_columns(selected, n):
                return selected

        # Fallback example for 4x4
        return [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1]
        ]

    def generate_all_possible_rows(self, n):
        return self.backtrack_row([], n, n//2, n//2)

    def backtrack_row(self, current, n, zeros, ones):
        if len(current) == n:
            return [current.copy()] if zeros == 0 and ones == 0 else []

        solutions = []
        for bit in [0, 1]:
            if (bit == 0 and zeros == 0) or (bit == 1 and ones == 0):
                continue

            if len(current) >= 2 and current[-1] == bit and current[-2] == bit:
                continue

            new_current = current.copy()
            new_current.append(bit)
            new_zeros = zeros - 1 if bit == 0 else zeros
            new_ones = ones - 1 if bit == 1 else ones
            solutions += self.backtrack_row(new_current, n, new_zeros, new_ones)

        return solutions

    def check_columns(self, grid, n):
        columns = list(zip(*grid))
        for col in columns:
            if col.count(0) != n//2 or col.count(1) != n//2:
                return False
            for i in range(len(col)-2):
                if col[i] == col[i+1] == col[i+2]:
                    return False
        return len(set(columns)) == len(columns)
