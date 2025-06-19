

### 谜题描述

**Objective**: Clear a rectangular grid of hidden cells without detonating any mines. Cells contain either mines or numbers indicating adjacent mines.

**Grid Setup**:
1. The grid consists of hidden cells, some containing mines (randomly placed).
2. Non-mine cells reveal a number when uncovered, representing the total mines in the 8 adjacent cells (vertically, horizontally, and diagonally).

**Gameplay**:
1. **Uncover a Cell**: Click/select a cell to reveal its content:
   - If it contains a mine, the game ends (loss).
   - If it shows a number, use this to deduce nearby mine locations.
   - If it shows **0** (no adjacent mines), all adjacent cells automatically uncover recursively until numbered cells are reached.

2. **Flagging Mines**: Right-click/mark a cell to flag it as a suspected mine (prevents accidental uncovering). Flags help track potential mines but do not affect gameplay logic otherwise.

**Win Condition**:
- All non-mine cells are uncovered, and all mines are correctly flagged.

**Logic Rules**:
- Numbers on the grid are **static hints**, not live updates. Flagging a mine does not change existing numbers.
- Use the numbers to infer mine positions: e.g., a cell labeled \"3\" must have exactly 3 mines in its 8 neighboring cells.

**Loss Condition**:
- Uncovering any cell containing a mine.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import ast

class Minesweeperbootcamp(Basebootcamp):
    def __init__(self, rows=8, cols=8, mines_count=10):
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
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_match)
            if (isinstance(solution, list) and 
                all(isinstance(coord, list) and len(coord) == 2 for coord in solution)):
                return solution
            return None
        except (SyntaxError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list):
            return False
        try:
            solution_set = {tuple(coord) for coord in solution}
        except TypeError:
            return False
        mines = identity.get('mines', [])
        mines_set = {tuple(mine) for mine in mines}
        if len(solution_set) != len(mines_set):
            return False
        rows, cols = identity['rows'], identity['cols']
        for (r, c) in solution_set:
            if not (0 <= r < rows and 0 <= c < cols):
                return False
        return solution_set == mines_set
