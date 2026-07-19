"""### 谜题描述

**Tapa Puzzle Rules**  

**Objective**: Blacken cells on a grid to satisfy all clues while adhering to connectivity and area constraints.  

1. **Clues**:  
   - Each white cell containing a clue has one or more numbers (e.g., \"3\", \"1 2\").  
   - Numbers represent the lengths of **orthogonally connected black cell groups** in the 8 surrounding cells (up, down, left, right, and diagonals).  
   - Multiple numbers (e.g., \"2 1\") indicate **separate groups**, each isolated by at least one white cell.  

2. **Group Formation**:  
   - A \"group\" is a set of black cells connected orthogonally (horizontally/vertically), **not diagonally**.  
   - Example: A clue \"3\" requires three orthogonally connected black cells in its perimeter. A clue \"1 2\" requires one isolated black cell and a separate pair of orthogonally connected black cells.  

3. **Global Constraints**:  
   - **Single Connected Region**: All black cells must form one connected area (diagonals allowed for connectivity).  
   - **No 2×2 Black Blocks**: No 2×2 square can be entirely black.  
   - **No Isolation**: White cells must not be fully enclosed by black cells (i.e., all white cells must be reachable from the grid’s edges).  

**Key Notes**:  
- Clue cells themselves remain **white**.  
- Numbers in clues can appear in any order (e.g., \"1 2\" and \"2 1\" are equivalent).  
- A clue cell with \"0\" means none of its 8 surrounding cells are black.  


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
from collections import deque
import json

class Tapabootcamp(Basebootcamp):
    def __init__(self, rows=5, cols=5):
        super().__init__()
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        # 示例解：中间为黑，其他为白
        solution = [[False for _ in range(self.cols)] for _ in range(self.rows)]
        center_r, center_c = self.rows//2, self.cols//2
        solution[center_r][center_c] = True
        
        clues = {}
        for r in range(self.rows):
            for c in range(self.cols):
                if not solution[r][c]:
                    groups = self.get_clue_numbers(solution, r, c, self.rows, self.cols)
                    if groups != [0]:
                        clues[f"{r},{c}"] = groups
        
        return {
            'rows': self.rows,
            'cols': self.cols,
            'clues': clues
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        rows = question_case['rows']
        cols = question_case['cols']
        clues = question_case['clues']
        prompt = "You are a solver for Tapa puzzles. Your task is to blacken cells in a grid according to the given clues and rules.\n\n"
        prompt += "**Rules**:\n"
        prompt += "- Each clue is a white cell with numbers indicating the lengths of orthogonally connected black cell groups in the surrounding 8 cells.\n"
        prompt += "- Multiple numbers indicate separate groups, each isolated by at least one white cell.\n"
        prompt += "- All black cells must form a single connected region (diagonally allowed).\n"
        prompt += "- No 2×2 area can be entirely black.\n"
        prompt += "- White cells must not be enclosed by black cells; they must be reachable from the grid's edge.\n\n"
        prompt += f"The puzzle grid is {rows}x{cols}. The clues are as follows:\n"
        for r_c, numbers in clues.items():
            row, col = map(int, r_c.split(','))
            nums_str = ' '.join(map(str, numbers))
            prompt += f"- Cell at row {row}, column {col}: {nums_str}\n"
        prompt += "\nYour answer should be a 2D list where each element is True (black) or False (white), enclosed within [answer] tags. For example:\n[answer]\n[[False, True], [True, False]]\n[/answer]"
        return prompt
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = eval(last_match)
            if isinstance(solution, list) and all(isinstance(row, list) for row in solution):
                return solution
            return None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        rows = identity['rows']
        cols = identity['cols']
        clues = identity['clues']
        
        if not isinstance(solution, list) or len(solution) != rows:
            return False
        for row in solution:
            if not isinstance(row, list) or len(row) != cols:
                return False
        
        for r_c, numbers in clues.items():
            row, col = map(int, r_c.split(','))
            if solution[row][col]:
                return False
            computed = cls.get_clue_numbers(solution, row, col, rows, cols)
            if sorted(numbers) != sorted(computed):
                return False
        
        black_cells = [(r, c) for r in range(rows) for c in range(cols) if solution[r][c]]
        if black_cells:
            if not cls.is_connected(black_cells, rows, cols):
                return False
        
        for r in range(rows - 1):
            for c in range(cols - 1):
                if solution[r][c] and solution[r][c+1] and solution[r+1][c] and solution[r+1][c+1]:
                    return False
        
        white_cells = [(r, c) for r in range(rows) for c in range(cols) if not solution[r][c]]
        if not white_cells:
            return False
        
        visited = set()
        queue = deque()
        for (r, c) in white_cells:
            if r == 0 or r == rows-1 or c == 0 or c == cols-1:
                if (r, c) not in visited:
                    queue.append((r, c))
                    visited.add((r, c))
        
        while queue:
            r, c = queue.popleft()
            for dr, dc in [(-1,0), (1,0), (0,1), (0,-1)]:
                nr, nc = r + dr, c + dc
                if 0 <= nr < rows and 0 <= nc < cols:
                    if not solution[nr][nc] and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        
        if any((r, c) not in visited for (r, c) in white_cells):
            return False
        
        return True
    
    @staticmethod
    def get_clue_numbers(solution, row, col, rows, cols):
        if solution[row][col]:
            return []
        
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, -1),          (0, 1),
                      (1, -1),  (1, 0), (1, 1)]
        adjacent = []
        for dr, dc in directions:
            r = row + dr
            c = col + dc
            if 0 <= r < rows and 0 <= c < cols:
                adjacent.append((r, c))
        
        black_cells = [(r, c) for (r, c) in adjacent if solution[r][c]]
        if not black_cells:
            return [0]
        
        visited = set()
        groups = []
        for (r, c) in black_cells:
            if (r, c) not in visited:
                queue = deque([(r, c)])
                visited.add((r, c))
                size = 1
                while queue:
                    x, y = queue.popleft()
                    for dx, dy in [(-1,0), (1,0), (0,1), (0,-1)]:
                        nx, ny = x + dx, y + dy
                        if (nx, ny) in black_cells and (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny))
                            size += 1
                groups.append(size)
        
        groups.sort()
        return groups if groups else [0]
    
    @classmethod
    def is_connected(cls, cells, rows, cols):
        if not cells:
            return True
        
        start = cells[0]
        visited = set([start])
        queue = deque([start])
        
        while queue:
            r, c = queue.popleft()
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if (nr, nc) in cells and (nr, nc) not in visited:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
        
        return len(visited) == len(cells)
