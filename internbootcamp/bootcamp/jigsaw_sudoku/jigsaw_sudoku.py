

### 谜题描述

Jigsaw Sudoku follows core Sudoku principles but replaces traditional fixed rectangular regions (\"boxes\") with irregularly shaped, contiguous regions (\"pieces\"). The rules are:

1. **Grid Structure**: The puzzle is played on an n×n grid, divided into n distinct regions. Each region must contain exactly n cells.

2. **Row and Column Rules**: Every row and column must contain all numbers from 1 to n exactly once (no duplicates, no omissions).

3. **Region Rule**: Each irregularly shaped region must also contain all numbers from 1 to n exactly once, with no repeats.

4. **Region Properties**: 
   - Regions can vary in shape (non-rectangular, \"jigsaw-like\").
   - All regions are contiguous (cells are connected edge-to-edge).
   - Regions do not overlap and fully partition the grid.

The challenge lies in satisfying all three constraints (rows, columns, and irregular regions) simultaneously. The grid size (n) is typically a perfect square (e.g., 4×4, 9×9), but the logic applies universally.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re

class JigsawSudokuV2bootcamp(Basebootcamp):
    def __init__(self, n=4, keep_prob=0.5):
        self.n = n
        self.keep_prob = keep_prob  # 保留下来的已知数字的比例
    
    def case_generator(self):
        # 示例固定区域结构和解（以4x4为例）
        n = self.n
        regions = [
            [[0,0], [0,1], [1,0], [2,0]],
            [[0,2], [0,3], [1,3], [2,3]],
            [[1,1], [1,2], [2,1], [2,2]],
            [[3,0], [3,1], [3,2], [3,3]]
        ]
        solution = [
            [1, 3, 4, 2],
            [4, 2, 1, 3],
            [2, 4, 3, 1],
            [3, 1, 2, 4]
        ]
        # 生成谜题实例，挖空部分单元格
        puzzle = []
        for row in solution:
            puzzle_row = []
            for num in row:
                if random.random() > self.keep_prob:
                    puzzle_row.append(None)
                else:
                    puzzle_row.append(num)
            puzzle.append(puzzle_row)
        return {
            'n': n,
            'regions': regions,
            'puzzle': puzzle,
            'solution': solution
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        regions = question_case['regions']
        puzzle = question_case['puzzle']
        
        # 生成区域结构描述
        region_grid = [[-1]*n for _ in range(n)]
        for idx, cells in enumerate(regions):
            for (r, c) in cells:
                region_grid[r][c] = idx
        
        region_str = "区域结构（每个单元格显示所属区域的编号）：\n"
        region_str += '\n'.join([' '.join(map(str, row)) for row in region_grid])
        
        # 生成谜题表格
        puzzle_str = "初始谜题（空格用_表示）：\n"
        for row in puzzle:
            puzzle_row = ['_' if num is None else str(num) for num in row]
            puzzle_str += ' '.join(puzzle_row) + '\n'
        
        # 构建完整提示
        prompt = f"""你是一名Jigsaw Sudoku玩家，请根据以下信息解答谜题：

谜题规则：
1. 每一行必须包含数字1到{n}，每个数字恰好一次。
2. 每一列必须包含数字1到{n}，每个数字恰好一次。
3. 每个不规则区域（由下方区域结构定义）必须包含数字1到{n}，每个数字恰好一次。

{region_str}

{puzzle_str}

请将完整解答按行排列，每行数字以逗号分隔，放在[answer]和[/answer]之间。例如：
[answer]
1,3,4,2
4,2,1,3
2,4,3,1
3,1,2,4
[/answer]
"""
        return prompt
    
    @staticmethod
    def extract_output(output):
        # 使用正则匹配最后一个答案块
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        last_answer = answer_blocks[-1].strip()
        solution = []
        for line in last_answer.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                solution.append([int(num) for num in line.split(',')])
            except:
                return None
        return solution if solution else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        puzzle = identity['puzzle']
        regions = identity['regions']
        
        # 检查已知数字是否匹配
        for r in range(n):
            for c in range(n):
                if puzzle[r][c] is not None and solution[r][c] != puzzle[r][c]:
                    return False
        
        # 验证行
        for row in solution:
            if sorted(row) != list(range(1, n+1)):
                return False
        
        # 验证列
        for c in range(n):
            if sorted(solution[r][c] for r in range(n)) != list(range(1, n+1)):
                return False
        
        # 验证区域
        for region in regions:
            region_numbers = [solution[r][c] for (r, c) in region]
            if sorted(region_numbers) != list(range(1, n+1)):
                return False
        
        return True
