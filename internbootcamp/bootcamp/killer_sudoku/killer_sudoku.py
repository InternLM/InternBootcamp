

### 谜题描述

Killer Sudoku is a logic puzzle that combines elements of Sudoku and Kakuro. The core rules are:

1. **Grid Structure**: Played on a standard Sudoku grid (typically 9x9), divided into smaller subgrids (e.g., 3x3 regions). Each row, column, and subgrid must contain all digits from 1 to the grid size (e.g., 1-9) exactly once, adhering to classic Sudoku rules.

2. **Cages**: The grid includes outlined groups of cells (\"cages\") marked with a target sum. 
   - Digits within a cage must be unique, even if the cage spans multiple rows, columns, or subgrids.
   - The sum of all digits in a cage must equal the specified target.

3. **No Overlaps**: Cages do not overlap, and every cell belongs to exactly one cage. Cages vary in size (from 1 cell to larger groupings) and shape.

4. **Combined Constraints**: Solutions must satisfy **both** the Sudoku rules (no repeats in rows, columns, subgrids) **and** the cage sum/uniqueness rules simultaneously.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from itertools import product

class Killersudokubootcamp(Basebootcamp):
    def __init__(self, size=9, subgrid_size=3):
        self.size = size
        self.subgrid_size = subgrid_size
        assert subgrid_size ** 2 == size, "Size must be a perfect square."
    
    def case_generator(self):
        solution = self.generate_sudoku_solution()
        cages = self.generate_cages(solution)
        return {
            "solution": solution,
            "cages": cages,
            "size": self.size,
            "subgrid_size": self.subgrid_size
        }
    
    def generate_sudoku_solution(self):
        size = self.size
        subgrid_size = self.subgrid_size
        grid = [[0 for _ in range(size)] for _ in range(size)]
        
        def is_valid(x, y, num):
            # Check row
            if num in grid[x]:
                return False
            # Check column
            for row in grid:
                if row[y] == num:
                    return False
            # Check subgrid
            start_x = (x // subgrid_size) * subgrid_size
            start_y = (y // subgrid_size) * subgrid_size
            for i in range(subgrid_size):
                for j in range(subgrid_size):
                    if grid[start_x + i][start_y + j] == num:
                        return False
            return True
        
        def backtrack(pos=0):
            if pos == size * size:
                return True
            row = pos // size
            col = pos % size
            if grid[row][col] != 0:
                return backtrack(pos + 1)
            nums = list(range(1, size + 1))
            random.shuffle(nums)
            for num in nums:
                if is_valid(row, col, num):
                    grid[row][col] = num
                    if backtrack(pos + 1):
                        return True
                    grid[row][col] = 0
            return False
        
        backtrack(0)
        return grid
    
    def generate_cages(self, solution):
        size = self.size
        used = [[False for _ in range(size)] for _ in range(size)]
        cages = []
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        for i in range(size):
            for j in range(size):
                if not used[i][j]:
                    cage_size = random.choices([1, 2], weights=[0.3, 0.7], k=1)[0]
                    current_cells = [(i, j)]
                    used[i][j] = True
                    current_values = {solution[i][j]}
                    
                    for _ in range(cage_size - 1):
                        neighbors = []
                        for (x, y) in current_cells:
                            for dx, dy in directions:
                                nx, ny = x + dx, y + dy
                                if 0 <= nx < size and 0 <= ny < size and not used[nx][ny]:
                                    val = solution[nx][ny]
                                    if val not in current_values:
                                        neighbors.append((nx, ny))
                        if not neighbors:
                            break
                        nx, ny = random.choice(neighbors)
                        current_cells.append((nx, ny))
                        used[nx][ny] = True
                        current_values.add(solution[nx][ny])
                    
                    cage_sum = sum(solution[x][y] for (x, y) in current_cells)
                    cages.append({
                        "cells": current_cells,
                        "sum": cage_sum
                    })
        return cages
    
    @staticmethod
    def prompt_func(question_case):
        cages = question_case["cages"]
        size = question_case["size"]
        subgrid_size = question_case["subgrid_size"]
        cage_descriptions = []
        
        for idx, cage in enumerate(cages):
            cells = cage["cells"]
            coords = ", ".join(f"({x+1}, {y+1})" for (x, y) in cells)
            cage_descriptions.append(f"Cage {idx+1}: Cells {coords} sum to {cage['sum']}.")
        
        prompt = f"""You are solving a Killer Sudoku puzzle on a {size}x{size} grid. The rules are:

1. **Standard Sudoku**: Each row, column, and {subgrid_size}x{subgrid_size} subgrid must contain numbers 1-{size} exactly once.
2. **Cage Rules**: Each cage's numbers must be unique and sum to its target.

Cages and their targets:
""" + "\n".join(cage_descriptions) + """

Fill the grid adhering to both rules. Format your answer as a {size}x{size} grid with each row as comma-separated numbers. Enclose it within [answer] and [/answer].

Example:
[answer]
1,2,3,4
3,4,1,2
2,1,4,3
4,3,2,1
[/answer]"""
        return prompt
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            grid = []
            for line in last_answer.split('\n'):
                line = line.strip()
                if line:
                    row = list(map(int, line.split(',')))
                    grid.append(row)
            return grid
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        size = identity['size']
        subgrid_size = identity['subgrid_size']
        cages = identity['cages']
        
        # Check Sudoku rules
        expected = set(range(1, size + 1))
        # Rows and columns
        for i in range(size):
            if set(solution[i]) != expected:
                return False
            if set(solution[j][i] for j in range(size)) != expected:
                return False
        # Subgrids
        for x in range(0, size, subgrid_size):
            for y in range(0, size, subgrid_size):
                subgrid = []
                for i in range(subgrid_size):
                    for j in range(subgrid_size):
                        subgrid.append(solution[x+i][y+j])
                if set(subgrid) != expected:
                    return False
        
        # Check cage rules
        for cage in cages:
            cells = cage['cells']
            values = [solution[x][y] for x, y in cells]
            if len(set(values)) != len(values) or sum(values) != cage['sum']:
                return False
        return True
