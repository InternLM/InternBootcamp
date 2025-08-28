"""### 谜题描述

The Aquarium puzzle is solved by determining water levels for each aquarium region in a grid, adhering to the following rules:

1. **Grid Structure**: The grid is divided into contiguous regions (aquariums) by thick borders. Each cell belongs to exactly one aquarium.

2. **Water Levels**: Each aquarium must be filled with water up to a consistent horizontal level. This level is a specific row number chosen such that:
   - Every column within the aquarium contains cells up to at least this row (i.e., the level cannot exceed the shortest column height in the aquarium).
   - All cells in the aquarium’s columns from the bottom row up to the chosen level are filled. Cells above this level in the aquarium remain empty.

3. **Row and Column Clues**: 
   - Numbers on the right side of each row indicate the total number of filled cells required in that row across all aquariums.
   - Numbers at the bottom/top of each column indicate the total number of filled cells required in that column across all aquariums.

4. **Objective**: Fill cells to satisfy all row/column numerical clues while ensuring each aquarium’s water level is uniformly applied to its columns.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from typing import Dict, List, Optional

class Aquariumbootcamp(Basebootcamp):
    def __init__(self, grid_rows: int = 5, grid_cols: int = 5):
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
    
    @staticmethod
    def extract_output(output: str) -> Optional[List[int]]:
        # Find all answer blocks
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        # Take the last match
        last_match = matches[-1].strip()
        try:
            solution = list(map(int, last_match.split()))
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution: List[int], identity: Dict) -> bool:
        cols = len(identity['col_clues'])
        rows = len(identity['row_clues'])
        # Check solution length matches columns
        if len(solution) != cols:
            return False
        # Check each column's solution matches column clue
        for c in range(cols):
            if solution[c] + 1 != identity['col_clues'][c]:
                return False
        # Check each row's filled count matches row clue
        for r in range(rows):
            expected = identity['row_clues'][r]
            actual = sum(1 for c in range(cols) if solution[c] >= r)
            if actual != expected:
                return False
        return True
