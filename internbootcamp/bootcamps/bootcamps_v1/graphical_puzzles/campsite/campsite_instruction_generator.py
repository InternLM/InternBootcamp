import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import ast
import json
import sys
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.lib.campsite_generator import generate_campsite
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.lib.campsite_validor import validate_campsite_solution




class CampsiteInstructionGenerator(BaseInstructionGenerator):
    """Campsite Bootcamp指令生成器"""
    
    def __init__(self, size:tuple = (8,8), expect_camp_number:int = 8, random_rate:float = 0.1):
        """
        初始化Campsite指令生成器
        
        Args:
            size: 参数描述
            expect_camp_number: 参数描述
            random_rate: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()   
        self.size = size
        self.expect_camp_number = expect_camp_number
        self.random_rate = random_rate
    
    def case_generator(self):
        grid, row_constraints, col_constraints = self.generator(self.size,self.expect_camp_number, self.random_rate )
        
        # ans, output, all_ans= self.env.solver()    
        
        # self.env.reset()
        
        return {
            'input_grid': grid,
            'row_constraints': row_constraints,
            'col_constraints': col_constraints
        }
    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """

        statements = [f"""You are an intelligent assistant specializing in solving custom puzzle problems. Below is a specific rule defined for a custom puzzle. Your task is to apply this rule accurately to the provided question.

    ### Instructions:
    
    1. Thoroughly understand the rule provided. If needed, break down the rule into simpler components or steps.
    2. Apply the rule carefully to address the question presented.
    3. Verify your answer to ensure it aligns with the rule and the context of the puzzle.
    
### Campsite Puzzle Rule:

1.The game is played on an n*m grid with trees at some locations in the grid.
2.To place tents on the grid.
3.Each tent must be orthogonally adjacent to a tree (i.e., above, below, to the left, or to the right of the tree).
4.Tents cannot be orthogonally or diagonally adjacent to other tents.
5.Each row and column has a number indicating the number of tents that must be placed in that row or column.
6.Each puzzle has and has only one unique solution.
7.The puzzle is given by a matrix in the form of T, which represents the position of the tree, and X, which represents the spaces,To the right and below the matrix are numerical constraints, and you need to replace X with C (for tents) for some spaces, and the answer is a matrix.

### Question

Now the gird of the Campsite is:\n{identity['input_grid']}
The row constraints is {identity['row_constraints']} and the col constraints is {identity['col_constraints']}.
""",        
f"""The Campsite is a puzzle game. The rule of Campsite is:
1.The game is played on an n*m grid with trees at some locations in the grid.
2.To place tents on the grid.
3.Each tent must be orthogonally adjacent to a tree (i.e., above, below, to the left, or to the right of the tree).
4.Tents cannot be orthogonally or diagonally adjacent to other tents.
5.Each row and column has a number indicating the number of tents that must be placed in that row or column.
6.Each puzzle has and has only one unique solution.
7.The puzzle is given by a matrix in the form of T, which represents the position of the tree, and X, which represents the spaces,To the right and below the matrix are numerical constraints, and you need to replace X with C (for tents) for some spaces, and the answer is a matrix.

Now the gird of the Campsite is:\n{identity['input_grid']}
The row constraints is {identity['row_constraints']} and the col constraints is {identity['col_constraints']}.
"""
]

        instruction_following = """
Let's think step by step and output the final answer with an example json formatting 
Final-answer: ```json
[['T', 'X', 'X', 'X'], ['X', 'T', 'X', 'X'], ['T', 'X', 'X', 'T'], ['X', 'X', 'X', 'X']]
```
"""

        return statements[random.randint(0,len(statements)-1)] + instruction_following 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generator(self, size:tuple = (8,8), expect_camp_number:int = 8, random_rate:float = 0.1 , seed:int = None):
        if size[0] < 2 and size[1] < 2:
            raise ValueError
        self.grid, self.row_constraints, self.col_constraints, self.refer_ans = generate_campsite(size[0], size[1], expect_camp_number, seed=seed, random_rate=random_rate)
        return self.grid, self.row_constraints, self.col_constraints    

    @staticmethod
    def check_solution(parsed_question: dict, parsed_response: dict) -> bool:
        original_grid = parsed_question['input_grid']
        expected_rows = parsed_question['row_constraints']
        expected_cols = parsed_question['col_constraints']
        solution = parsed_response

        n, m = len(original_grid), len(original_grid[0]) if original_grid else 0

        # Check dimensions
        if len(solution) != n or any(len(row) != m for row in solution):
            return False

        tents = []
        # Check T positions and collect tents
        for i in range(n):
            for j in range(m):
                orig = original_grid[i][j]
                sol = solution[i][j]
                if orig == 'T':
                    if sol != 'T':
                        return False
                else:
                    if sol not in ('X', 'C'):
                        return False
                    if sol == 'C':
                        tents.append((i, j))

        # Check tents adjacency to trees and other tents
        directions_ortho = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for i, j in tents:
            has_tree = False
            for dx, dy in directions_ortho:
                x, y = i + dx, j + dy
                if 0 <= x < n and 0 <= y < m and solution[x][y] == 'T':
                    has_tree = True
                    break
            if not has_tree:
                return False

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    x, y = i + dx, j + dy
                    if 0 <= x < n and 0 <= y < m and (x, y) in tents:
                        return False

        # Check row constraints
        for i in range(n):
            if sum(1 for cell in solution[i] if cell == 'C') != expected_rows[i]:
                return False

        # Check column constraints
        for j in range(m):
            if sum(1 for i in range(n) if solution[i][j] == 'C') != expected_cols[j]:
                return False

        return True
