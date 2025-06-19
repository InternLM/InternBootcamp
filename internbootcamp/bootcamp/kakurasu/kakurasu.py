

### 谜题描述

Kakurasu is a logic puzzle played on a rectangular grid (typically N×N). Each cell in the grid can be either shaded or unshaded. The puzzle provides target values for each row and column, and the goal is to shade cells such that:

1. **Row Constraints**: For every row, the sum of the *column indices* of the shaded cells in that row equals the target value specified for that row.  
   - Example: If a row's target is 7, you might shade cells in columns 3 and 4 (since 3 + 4 = 7).

2. **Column Constraints**: For every column, the sum of the *row indices* of the shaded cells in that column equals the target value specified for that column.  
   - Example: If a column's target is 5, you might shade cells in rows 2 and 3 (since 2 + 3 = 5).

3. **Unique Contributions**: A shaded cell at position (row *i*, column *j*) contributes its *column index* **j** to its row's sum and its *row index* **i** to its column's sum. These dual contributions must satisfy both the row and column targets simultaneously.

4. **No Overlapping Rules**: Unlike Sudoku, there are no region constraints—only row and column sums matter. However, cells cannot be \"partially\" shaded; they are either fully shaded or unshaded.

The puzzle is solved when all row and column targets are satisfied without contradiction.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import ast

class Kakurasubootcamp(Basebootcamp):
    def __init__(self, n=5):
        self.n = n
    
    def case_generator(self):
        n = self.n
        grid = [[random.choice([0, 1]) for _ in range(n)] for _ in range(n)]
        
        row_targets = []
        for i in range(n):
            total = sum((j + 1) * cell for j, cell in enumerate(grid[i]))
            row_targets.append(total)
        
        col_targets = []
        for j in range(n):
            total = sum((i + 1) * grid[i][j] for i in range(n))
            col_targets.append(total)
        
        return {
            'n': n,
            'row_targets': row_targets,
            'col_targets': col_targets
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        row_targets = question_case['row_targets']
        col_targets = question_case['col_targets']
        return f"""你正在解决一个Kakurasu谜题。这是一个{n}x{n}的网格谜题，目标是根据行和列的约束条件涂黑单元格。

规则：
1. 每行中被涂黑单元格的列索引（从左到右为1到{n}）之和等于该行的目标值。
2. 每列中被涂黑单元格的行索引（从上到下为1到{n}）之和等于该列的目标值。
3. 每个单元格必须明确涂黑（1）或未涂黑（0）。

当前谜题的行目标值（从上到下）：{row_targets}
当前谜题的列目标值（从左到右）：{col_targets}

请将你的解答格式化为{n}x{n}的二维数组，其中1表示涂黑，0表示未涂黑，并用[answer]和[/answer]标签包裹。例如：
[answer]
[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
[/answer]
"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_match)
            return solution
        except (SyntaxError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        row_targets = identity['row_targets']
        col_targets = identity['col_targets']
        
        # 验证答案结构
        if not isinstance(solution, list) or len(solution) != n:
            return False
        for row in solution:
            if not isinstance(row, list) or len(row) != n:
                return False
            for cell in row:
                if cell not in (0, 1):
                    return False
        
        # 验证行约束
        for i in range(n):
            row_sum = sum((j + 1) * cell for j, cell in enumerate(solution[i]))
            if row_sum != row_targets[i]:
                return False
        
        # 验证列约束
        for j in range(n):
            col_sum = sum((i + 1) * solution[i][j] for i in range(n))
            if col_sum != col_targets[j]:
                return False
        
        return True
