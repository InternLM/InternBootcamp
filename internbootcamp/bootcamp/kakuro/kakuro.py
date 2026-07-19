"""### 谜题描述

**Kakuro Puzzle Rules:**

1. **Grid Structure**:  
   - The puzzle is played on a grid of white (empty) and black (clue) cells.  
   - **Clue cells** (black) contain hints for solving adjacent white cells. Each clue has two components:  
     - **Rightward (→)**: Sum of digits in the horizontal sequence of white cells to its right.  
     - **Downward (↓)**: Sum of digits in the vertical sequence of white cells below it.  

2. **Digit Placement**:  
   - Fill white cells with digits **1–9**.  
   - A digit **cannot repeat** within the same horizontal or vertical sequence (referred to as a \"run\").  

3. **Run Constraints**:  
   - Each run is defined by a clue cell. For example, a rightward clue of \"12 in 3 cells\" means the three adjacent horizontal cells must sum to 12, with no repeated digits.  
   - A white cell can belong to both a horizontal and vertical run simultaneously. Its digit must satisfy **both clues**.  

4. **Key Principles**:  
   - **Uniqueness**: All digits in a single run must be distinct.  
   - **No Zeros**: Digits must be between 1 and 9.  
   - **Interconnected Solutions**: Solving one run provides constraints for intersecting runs.  

**Objective**: Fill all white cells to satisfy all horizontal and vertical clues without violating the rules.  


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from ast import literal_eval

class Kakurobootcamp(Basebootcamp):
    def __init__(self, rows=3, cols=3):
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        # 生成横向序列的数对
        a, b = self._generate_unique_pair()
        sum_r = a + b
        
        # 生成纵向序列的数对
        c, d = self._generate_unique_pair()
        sum_d = c + d
        
        # 构建网格结构
        grid = [[{'type': 'black', 'right': (sum_r, 2), 'down': (sum_d, 2)} if (row == 0 and col == 0) else
                {'type': 'white'} if ((row == 0 and col in (1, 2)) or (col == 0 and row in (1, 2))) else
                {'type': 'black'} for col in range(self.cols)] for row in range(self.rows)]
        
        solution = {
            "(0, 1)": a,
            "(0, 2)": b,
            "(1, 0)": c,
            "(2, 0)": d
        }
        
        return {
            'grid': grid,
            'solution': solution
        }
    
    def _generate_unique_pair(self):
        while True:
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            if a != b:
                return a, b
    
    @staticmethod
    def prompt_func(question_case) -> str:
        clues = []
        grid = question_case['grid']
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                if cell['type'] == 'black':
                    parts = []
                    if 'right' in cell:
                        sum_r, len_r = cell['right']
                        parts.append(f"右侧的 {len_r} 个白色格子之和为 {sum_r}")
                    if 'down' in cell:
                        sum_d, len_d = cell['down']
                        parts.append(f"下方的 {len_d} 个白色格子之和为 {sum_d}")
                    if parts:
                        clues.append(f"位于 ({row_idx}, {col_idx}) 的黑色格子：" + "，".join(parts))
        clues_text = "\n".join(clues)
        
        white_coords = []
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                if cell['type'] == 'white':
                    white_coords.append(f"({row_idx}, {col_idx})")
        white_coords_text = ", ".join(white_coords)
        
        prompt = f"""你是Kakuro谜题解答者，请根据以下线索填充所有白色格子，确保每个横向或纵向的序列满足和的条件，且同一序列中的数字不重复。每个格子只能填1-9的整数。

谜题线索：
{clues_text}

需要填充的白色格子位于以下坐标：{white_coords_text}。

请将你的答案以字典形式放在[answer]和[/answer]之间，键为坐标字符串，如"(行,列)"，值为对应的整数。例如：
[answer]
{{"(0,1)": 3, "(0,2)": 4, "(1,0)":5, "(2,0)":2}}
[/answer]
请确保所有白色格子都被正确填写，且没有多余或缺少的项。"""
        return prompt
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_block = answer_blocks[-1].strip()
        try:
            answer_dict = literal_eval(last_block)
            if not isinstance(answer_dict, dict):
                return None
            converted = {}
            for coord_str, value in answer_dict.items():
                coord_str = coord_str.strip('()')
                row, col = map(int, coord_str.split(','))
                converted[(row, col)] = value
            return converted
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        grid = identity['grid']
        solution = solution.copy()
        
        # Check all coordinates in solution are valid white cells
        for coord in solution:
            row, col = coord
            if row < 0 or col < 0 or row >= len(grid) or col >= len(grid[0]):
                return False
            cell = grid[row][col]
            if cell.get('type') != 'white':
                return False
            value = solution[coord]
            if not (1 <= value <= 9):
                return False
        
        # Check all clues
        for row_idx in range(len(grid)):
            for col_idx in range(len(grid[row_idx])):
                cell = grid[row_idx][col_idx]
                if cell.get('type') != 'black':
                    continue
                # Check right clue
                if 'right' in cell:
                    sum_r, len_r = cell['right']
                    run_coords = []
                    current_col = col_idx + 1
                    while current_col < len(grid[row_idx]) and grid[row_idx][current_col].get('type') == 'white':
                        run_coords.append((row_idx, current_col))
                        current_col += 1
                    if len(run_coords) != len_r:
                        return False
                    # Check all coords are in solution
                    for coord in run_coords:
                        if coord not in solution:
                            return False
                    values = [solution[coord] for coord in run_coords]
                    if sum(values) != sum_r or len(set(values)) != len_r:
                        return False
                # Check down clue
                if 'down' in cell:
                    sum_d, len_d = cell['down']
                    run_coords = []
                    current_row = row_idx + 1
                    while current_row < len(grid) and grid[current_row][col_idx].get('type') == 'white':
                        run_coords.append((current_row, col_idx))
                        current_row += 1
                    if len(run_coords) != len_d:
                        return False
                    for coord in run_coords:
                        if coord not in solution:
                            return False
                    values = [solution[coord] for coord in run_coords]
                    if sum(values) != sum_d or len(set(values)) != len_d:
                        return False
        return True
