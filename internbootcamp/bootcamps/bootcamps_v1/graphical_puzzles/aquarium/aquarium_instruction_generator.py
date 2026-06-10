import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from typing import Dict
from typing import List
from typing import Optional




class AquariumInstructionGenerator(BaseInstructionGenerator):
    """Aquarium Bootcamp指令生成器"""
    
    def __init__(self, grid_rows: int = 5, grid_cols: int = 5):
        """
        初始化Aquarium指令生成器
        
        Args:
            grid_rows: 参数描述
            grid_cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.grid_rows = grid_rows
        self.grid_cols = grid_cols
    
    def case_generator(self) -> Dict:
        # Generate regions where each column is a separate aquarium
        cols = self.grid_cols
        rows = self.grid_rows
        regions = []
        for r in range(rows):
            regions.append([c for c in range(cols)])
        
        # Generate water levels for each column (aquarium)
        k = [random.randint(0, rows - 1) for _ in range(cols)]
        
        # Compute row clues: number of filled cells per row
        row_clues = []
        for r in range(rows):
            count = sum(1 for c in range(cols) if k[c] >= r)
            row_clues.append(count)
        
        # Column clues are k[i] + 1
        col_clues = [ki + 1 for ki in k]
        
        return {
            'regions': regions,
            'row_clues': row_clues,
            'col_clues': col_clues,
        }
    
    @staticmethod
    def prompt_func(question_case: Dict) -> str:
        rows = len(question_case['regions'])
        cols = len(question_case['regions'][0]) if rows > 0 else 0
        regions_table = '\n'.join([f"Row {i}: {' '.join(map(str, row))}" for i, row in enumerate(question_case['regions'])])
        row_clues = question_case['row_clues']
        col_clues = question_case['col_clues']
        
        prompt = f"""You are to solve an Aquarium puzzle. The puzzle is played on a grid divided into aquarium regions. Each aquarium must be filled up to a horizontal level such that all its columns are filled to the same level. Here are the details:

- The grid has {rows} rows and {cols} columns.

- Aquarium regions are as follows (each number represents the aquarium ID for that cell):
{regions_table}

- Each row has a clue on the right indicating the total filled cells in that row. The row clues are: {row_clues}.

- Each column has a clue at the bottom indicating the total filled cells in that column. The column clues are: {col_clues}.

Your task is to determine the water level for each aquarium. The water level is the highest row number filled (0-based from the bottom). Each aquarium's water level must be such that all its columns are filled up to this level.

Provide your answer as a list of integers in column order (from left to right), where each integer is the water level for the corresponding column's aquarium. Enclose your answer within [answer] and [/answer]. For example, if the solution is levels 2, 1, 0 for columns 0, 1, 2, write:
[answer]2 1 0[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

