

### 谜题描述

**Skyscrapers Puzzle Rules (General Form):**

1. **Grid Structure**:  
   - The puzzle is played on an N×N grid (e.g., 5×5, 6×6).  
   - Each cell must contain a number from 1 to N, representing the height of a \"skyscraper.\"  

2. **Core Rules**:  
   - **Unique Heights**: Each row and column must contain every number from 1 to N exactly once (similar to Sudoku).  
   - **Visibility Clues**: Numbers are provided on the edges of the grid, indicating how many skyscrapers are visible from that direction.  

3. **Visibility Definition**:  
   - A skyscraper is \"visible\" if it is taller than all buildings between it and the edge of the grid.  
   - Example: In a row with heights [3, 1, 4, 2], looking from the left, you see 3 (blocks 1) and 4 (blocks 2). The clue here would be **2**.  

4. **Clue Placement**:  
   - **Edge Clues**: Numbers outside the grid correspond to the count of visible skyscrapers when looking inward:  
     - **Top/Bottom**: Clues for columns (viewed top-to-bottom or bottom-to-top).  
     - **Left/Right**: Clues for rows (viewed left-to-right or right-to-left).  

5. **Objective**:  
   - Fill the grid so that all row/column uniqueness constraints are satisfied, and the visibility counts match the provided clues.  

**Key Idea**: Taller buildings block shorter ones behind them, and clues enforce how many \"peaks\" are observable from each edge.  


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re

class Skyscrapersbootcamp(Basebootcamp):
    def __init__(self, n=4):
        self.n = n
    
    def case_generator(self):
        n = self.n
        square = self.generate_latin_square(n)
        clues = {
            'left': [],
            'right': [],
            'top': [],
            'bottom': []
        }
        
        for row in square:
            clues['left'].append(self.compute_view(row))
            clues['right'].append(self.compute_view(row[::-1]))
        
        for j in range(n):
            column = [square[i][j] for i in range(n)]
            clues['top'].append(self.compute_view(column))
            clues['bottom'].append(self.compute_view(column[::-1]))
        
        return {'n': n, 'clues': clues}
    
    @staticmethod
    def generate_latin_square(n):
        square = []
        for i in range(n):
            row = [(i + j) % n + 1 for j in range(n)]
            square.append(row)
        random.shuffle(square)
        square = list(map(list, zip(*square)))
        random.shuffle(square)
        square = list(map(list, zip(*square)))
        return square
    
    @staticmethod
    def compute_view(view):
        max_h = -1
        count = 0
        for h in view:
            if h > max_h:
                count += 1
                max_h = h
        return count
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        clues = question_case['clues']
        example = "\n".join([" ".join(['1'] * n)] * n)
        prompt = (
            "你正在解决一个数织谜题（Skyscrapers Puzzle）。规则如下：\n"
            "1. 在{}×{}网格中填入1至{}，每行每列数字不重复。\n"
            "2. 周围数字表示从该方向能看到的摩天大楼数量（较高建筑会遮挡后面较矮的）。\n\n"
            "谜题线索：\n"
            "- 网格大小：{}×{}\n"
            "- 顶部线索（各列从上至下可见数）：{}\n"
            "- 底部线索（各列从下至上可见数）：{}\n"
            "- 左侧线索（各行从左至右可见数）：{}\n"
            "- 右侧线索（各行从右至左可见数）：{}\n\n"
            "请填入符合要求的网格，并将答案放在[answer]和[/answer]之间。格式示例：\n"
            "[answer]\n{}[/answer]"
        ).format(
            n, n, n, n, n,
            ' '.join(map(str, clues['top'])),
            ' '.join(map(str, clues['bottom'])),
            ' '.join(map(str, clues['left'])),
            ' '.join(map(str, clues['right'])),
            example
        )
        return prompt
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        solution_str = matches[-1].strip()
        solution = []
        for line in solution_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not all(part.isdigit() for part in parts):
                return None
            solution.append([int(part) for part in parts])
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        n = identity['n']
        clues = identity['clues']
        
        if len(solution) != n or any(len(row) != n for row in solution):
            return False
        
        for row in solution:
            if sorted(row) != list(range(1, n+1)):
                return False
        
        for col in range(n):
            column = [solution[row][col] for row in range(n)]
            if sorted(column) != list(range(1, n+1)):
                return False
        
        for i in range(n):
            row = solution[i]
            if (cls.compute_view(row) != clues['left'][i] or
                cls.compute_view(row[::-1]) != clues['right'][i]):
                return False
        
        for j in range(n):
            col = [solution[i][j] for i in range(n)]
            if (cls.compute_view(col) != clues['top'][j] or
                cls.compute_view(col[::-1]) != clues['bottom'][j]):
                return False
        
        return True
