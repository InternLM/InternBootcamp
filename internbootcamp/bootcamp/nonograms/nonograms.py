

### 谜题描述

Nonograms, also called \"Paint by Numbers,\" are logic puzzles where you reveal a hidden image by filling cells in a grid according to numerical clues. Here are the general rules:

1. **Grid Structure**:  
   - The puzzle consists of a rectangular grid (e.g., 10×10, 15×15, etc.).  
   - Each **row** and **column** has a sequence of numbers (clues) at its edge.

2. **Clue Interpretation**:  
   - Clues indicate groups of **consecutively filled cells** in that row/column.  
     Example: A clue of `3 2` means the row/column contains a block of 3 filled cells, followed by **at least one empty cell**, then a block of 2 filled cells.  
   - The **order of clues** matches the order of blocks (left-to-right for rows, top-to-bottom for columns).  
   - Empty cells can be marked with an \"X\" or left blank, depending on the puzzle variant.

3. **Rules for Filling**:  
   - **Exact blocks**: The numbers must correspond **exactly** to the filled cells.  
     Example: If a row has a clue `5`, the entire row must be filled with 5 contiguous cells.  
   - **No overlaps**: Blocks of filled cells cannot overlap unless the clues explicitly allow it (rare).  
   - **Separation**: Blocks in the same row/column must be separated by **at least one empty cell**.  

4. **Solving Logic**:  
   - Use **cross-referencing** between row and column clues to deduce filled cells.  
   - Eliminate impossible configurations using overlaps or forced gaps.  

5. **Victory Condition**:  
   - The puzzle is solved when all filled cells match the clues for every row and column, revealing the hidden image.  

Nonograms require no guessing—only logical deduction based on the clues and grid constraints.  


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re

class Nonogramsbootcamp(Basebootcamp):
    def __init__(self, **params):
        self.rows = params.get('rows', 5)
        self.cols = params.get('cols', 5)
        self.fill_prob = params.get('fill_prob', 0.3)

    def case_generator(self):
        # Generate solution grid
        solution = [
            [random.random() < self.fill_prob for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        # Calculate clues
        rows_clues = [self._get_clues(row) for row in solution]
        cols_clues = [self._get_clues([solution[r][c] for r in range(self.rows)]) 
                     for c in range(self.cols)]

        return {'rows': rows_clues, 'columns': cols_clues}

    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = """你正在解决一个Nonogram谜题。根据行和列的数字线索填充网格：

规则说明：
1. 数字表示连续填充的单元格块，块间至少间隔一个空格
2. 行线索从左到右排列，列线索从上到下排列
3. 用'X'表示填充，用空格或'.'表示空白

行线索：
""" + "\n".join(
    f"第{i+1}行: {clues if clues else '无'}" 
    for i, clues in enumerate(question_case['rows'])
) + "\n\n列线索：\n" + "\n".join(
    f"第{i+1}列: {clues if clues else '无'}" 
    for i, clues in enumerate(question_case['columns'])
) + """

请将最终答案放在[answer]标签内，每行用'X'和空格表示填充状态：
示例：
[answer]
XX X
 XXX
X  X
[/answer]"""
        return prompt

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        grid_str = matches[-1].strip()
        solution = []
        for line in grid_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            solution.append([c.upper() == 'X' for c in line if not c.isspace() or c == '.'])
        return solution

    @classmethod
    def _verify_correction(cls, solution, identity):
        # Validate grid dimensions
        if len(solution) != len(identity['rows']):
            return False
        if any(len(row) != len(identity['columns']) for row in solution):
            return False

        # Check row clues
        for i, row in enumerate(solution):
            if cls._get_clues(row) != identity['rows'][i]:
                return False

        # Check column clues
        for j in range(len(identity['columns'])):
            col = [solution[i][j] for i in range(len(solution))]
            if cls._get_clues(col) != identity['columns'][j]:
                return False

        return True

    @staticmethod
    def _get_clues(line):
        clues = []
        current = 0
        for cell in line:
            if cell:
                current += 1
            elif current > 0:
                clues.append(current)
                current = 0
        if current > 0:
            clues.append(current)
        return clues
