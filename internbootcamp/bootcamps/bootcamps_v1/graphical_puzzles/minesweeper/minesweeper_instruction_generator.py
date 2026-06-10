import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import ast




class MinesweeperInstructionGenerator(BaseInstructionGenerator):
    """Minesweeper Bootcamp指令生成器"""
    
    def __init__(self, rows=8, cols=8, mines_count=10):
        """
        初始化Minesweeper指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
            mines_count: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if mines_count > rows * cols:
            raise ValueError("Number of mines cannot exceed grid size.")
        self.rows = rows
        self.cols = cols
        self.mines_count = mines_count
    
    def case_generator(self):
        all_cells = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        if self.mines_count > len(all_cells):
            raise ValueError("mines_count exceeds valid cells count.")
        mines = random.sample(all_cells, self.mines_count)
        mines_list = [list(coord) for coord in mines]
        return {
            'rows': self.rows,
            'cols': self.cols,
            'mines': mines_list
        }
    
    @staticmethod
    def prompt_func(question_case):
        rows = question_case['rows']
        cols = question_case['cols']
        mines_count = len(question_case['mines'])
        mines_set = set(tuple(coord) for coord in question_case['mines'])
        
        grid_info = []
        for i in range(rows):
            for j in range(cols):
                count = 0
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        if dx == 0 and dy == 0:
                            continue
                        x, y = i + dx, j + dy
                        if 0 <= x < rows and 0 <= y < cols and (x, y) in mines_set:
                            count += 1
                grid_info.append((i, j, count))
        
        prompt = (
            f"You are playing Minesweeper on a {rows}x{cols} grid with {mines_count} mines.\n"
            "Each number below represents the count of adjacent mines for a cell. "
            "Find all the mine locations and provide them in the specified format.\n\n"
            "Revealed cells (format: row, column: count):\n"
        )
        for i, j, num in grid_info:
            prompt += f"- ({i}, {j}): {num}\n"
        prompt += (
            "\nYour answer must be a list of mine coordinates formatted as [[row1, col1], [row2, col2], ...]. "
            "Place your final answer between [answer] and [/answer]."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

