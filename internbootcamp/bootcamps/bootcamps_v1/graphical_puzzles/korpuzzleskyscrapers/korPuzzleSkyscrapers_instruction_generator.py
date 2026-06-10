import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class KorpuzzleskyscrapersInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzleskyscrapers Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Korpuzzleskyscrapers指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.n = params.get('n', 4)  # Default to 4x4 grid
    
    def case_generator(self):
        solution = self.generate_solution()
        left = [self.count_visible(row) for row in solution]
        right = [self.count_visible(reversed(row)) for row in solution]
        top = []
        bottom = []
        for col in range(self.n):
            column = [solution[row][col] for row in range(self.n)]
            top.append(self.count_visible(column))
            bottom.append(self.count_visible(reversed(column)))
        return {
            'n': self.n,
            'top': top,
            'bottom': bottom,
            'left': left,
            'right': right
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        grid_layout = "Grid Layout:\n"
        grid_layout += "\t" + "\t".join(map(str, question_case['top'])) + "\n"
        for i in range(n):
            left = question_case['left'][i]
            right = question_case['right'][i]
            x_part = "\t".join(['X'] * n)
            grid_layout += f"{left}\t{x_part}\t{right}\n"
        grid_layout += "\t" + "\t".join(map(str, question_case['bottom'])) + "\n"
        
        prompt = (
            "You are a city planner trying to arrange skyscrapers on an {n}x{n} grid. Each cell must contain a skyscraper with a height from 1 to {n}.\n"
            "The rules are:\n"
            "1. Each row and column must contain exactly one of each height (1-{n}).\n"
            "2. The numbers around the grid indicate how many skyscrapers are visible from that direction (taller buildings block shorter ones behind them).\n\n"
            "Given the following grid layout with visibility constraints:\n"
            "{grid_layout}\n"
            "Fill in the grid correctly. Format your answer as numbers arranged left to right, top to bottom, each row separated by a comma and space, enclosed in double square brackets.\n"
            "Example: [[1 2 3 4, 2 3 4 1, 3 4 1 2, 4 1 2 3]]\n"
        ).format(n=n, grid_layout=grid_layout)
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_solution(self):
        n = self.n
        # Generate base Latin square with shifted rows
        base = [[(i + j) % n + 1 for j in range(n)] for i in range(n)]
        random.shuffle(base)  # Shuffle rows

        # Shuffle columns
        cols = list(range(n))
        random.shuffle(cols)
        solution = []
        for row in base:
            new_row = [row[col] for col in cols]
            solution.append(new_row)

        # Additional row and column permutations for enhanced randomness
        for _ in range(n):
            i, j = random.sample(range(n), 2)
            solution[i], solution[j] = solution[j], solution[i]

        for _ in range(n):
            i, j = random.sample(range(n), 2)
            for row in solution:
                row[i], row[j] = row[j], row[i]

        return solution

    @staticmethod
    def count_visible(sequence):
        max_h, count = 0, 0
        for num in sequence:
            if num > max_h:
                count += 1
                max_h = num
        return count
