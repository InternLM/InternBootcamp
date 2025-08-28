"""### 谜题描述

Sudoku is a logic-based number placement puzzle played on a square grid divided into smaller subgrids (called \"regions\" or \"blocks\"). The rules are as follows:

1. **Grid Structure**:  
   - The puzzle grid is a square of size N×N, where N is a perfect square (e.g., 9×9, 16×16).  
   - The grid is subdivided into N smaller rectangular regions, each of size √N×√N. For example, a 9×9 grid has nine 3×3 regions.

2. **Number Placement**:  
   - The grid is partially filled with numbers (or symbols) at the start.  
   - The solver must fill every empty cell with a number from **1 to N** (or symbols equivalent in count to N).

3. **Core Rules**:  
   - **Row Constraint**: Each number must appear **exactly once** in every row.  
   - **Column Constraint**: Each number must appear **exactly once** in every column.  
   - **Region Constraint**: Each number must appear **exactly once** in every subgrid/region.  

The puzzle is solved when all cells are filled while satisfying all three constraints. No arithmetic or guessing is required—only logical deduction.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import math
import random
from typing import List, Optional

class Sudokubootcamp(Basebootcamp):
    def __init__(self, size: int = 9):
        """
        初始化数独训练场参数
        
        参数:
            size: 数独尺寸（必须为完全平方数，默认9）
        """
        sqrt_n = math.isqrt(size)
        if sqrt_n * sqrt_n != size:
            raise ValueError("Size必须为完全平方数")
        self.size = size
        self.sqrt_n = sqrt_n
    
    def case_generator(self) -> dict:
        """
        生成数独谜题实例
        
        返回包含以下信息的字典:
        - puzzle: 数独初始网格（0表示空格）
        - size: 数独尺寸
        - region_rows: 子区域行数
        - region_cols: 子区域列数（同region_rows）
        """
        # 生成完整解
        solution = self._generate_full_sudoku()
        
        # 挖空50%的格子（可根据需求调整比例）
        puzzle = self._dig_holes(solution.copy(), dig_prob=0.5)
        
        return {
            "puzzle": [row.copy() for row in puzzle],
            "size": self.size,
            "region_rows": self.sqrt_n,
            "region_cols": self.sqrt_n
        }

    @staticmethod
    def prompt_func(question_case: dict) -> str:
        """
        将数独实例转换为自然语言描述的问题
        
        参数:
            question_case: case_generator生成的谜题实例
            
        返回:
            包含规则说明和当前谜题状态的格式化字符串
        """
        puzzle = question_case["puzzle"]
        size = question_case["size"]
        region_size = question_case["region_rows"]
        
        prompt = f"""你是一个专业数独玩家，请解决以下{size}x{size}的数独谜题。规则要求：
1. 每行必须包含1-{size}所有数字，无重复
2. 每列必须包含1-{size}所有数字，无重复
3. 每个{region_size}x{region_size}的子区域必须包含1-{size}所有数字，无重复

当前谜题状态（0表示空格）：
"""
        for i, row in enumerate(puzzle):
            prompt += f"第{i+1}行：" + " ".join(str(n) if n != 0 else "▢" for n in row) + "\n"

        prompt += "\n请将完整解答按如下格式放在[answer]标记之间：\n[answer]\n1 2 3 ...\n4 5 6 ...\n...\n[/answer]"
        return prompt

    @staticmethod
    def extract_output(output: str) -> Optional[List[List[int]]]:
        """
        从模型输出中提取最后一个数独解
        
        参数:
            output: 包含[answer]标记的完整输出文本
            
        返回:
            二维整数矩阵，解析失败时返回None
        """
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
            
        try:
            solution = []
            for line in matches[-1].strip().split('\n'):
                nums = list(map(int, line.strip().split()))
                if nums:
                    solution.append(nums)
            return solution
        except:
            return None

    @classmethod
    def _verify_correction(cls, solution: List[List[int]], identity: dict) -> bool:
        """
        验证解的正确性
        
        参数:
            solution: 用户提交的解
            identity: 谜题实例信息
            
        返回:
            布尔值表示解的正确性
        """
        def is_valid_region(grid, row_start, col_start, size, region_size) -> bool:
            """验证子区域有效性"""
            nums = set()
            for i in range(row_start, row_start+region_size):
                for j in range(col_start, col_start+region_size):
                    num = grid[i][j]
                    if num < 1 or num > size or num in nums:
                        return False
                    nums.add(num)
            return True

        puzzle = identity["puzzle"]
        size = identity["size"]
        region_size = identity["region_rows"]
        
        # 基本维度检查
        if len(solution) != size or any(len(row) != size for row in solution):
            return False
        
        # 验证初始条件
        for i in range(size):
            for j in range(size):
                if puzzle[i][j] != 0 and solution[i][j] != puzzle[i][j]:
                    return False
        
        # 验证行、列、子区域
        valid_range = set(range(1, size+1))
        for i in range(size):
            if set(solution[i]) != valid_range:  # 行验证
                return False
            if set(solution[j][i] for j in range(size)) != valid_range:  # 列验证
                return False
            
        # 子区域验证
        for i in range(0, size, region_size):
            for j in range(0, size, region_size):
                if not is_valid_region(solution, i, j, size, region_size):
                    return False
        
        return True

    def _generate_full_sudoku(self) -> List[List[int]]:
        """生成有效完整数独的核心算法"""
        size = self.size
        region_size = self.sqrt_n
        grid = [[0]*size for _ in range(size)]
        
        # 填充对角线子区域
        for i in range(0, size, region_size):
            nums = list(range(1, size+1))
            random.shuffle(nums)
            for x in range(region_size):
                for y in range(region_size):
                    grid[i+x][i+y] = nums[x*region_size + y]
        
        # 解数独
        self._solve_sudoku(grid)
        return grid

    def _solve_sudoku(self, grid: List[List[int]]) -> bool:
        """回溯法解数独"""
        size = self.size
        region_size = self.sqrt_n
        empty = self._find_empty(grid)
        
        if not empty:
            return True
            
        row, col = empty
        for num in random.sample(range(1, size+1), size):  # 随机尝试增加多样性
            if self._is_safe(grid, row, col, num):
                grid[row][col] = num
                if self._solve_sudoku(grid):
                    return True
                grid[row][col] = 0
        return False

    def _find_empty(self, grid: List[List[int]]) -> Optional[tuple]:
        """寻找下一个空单元格"""
        for i in range(self.size):
            for j in range(self.size):
                if grid[i][j] == 0:
                    return (i, j)
        return None

    def _is_safe(self, grid: List[List[int]], row: int, col: int, num: int) -> bool:
        """检查数字是否可以安全填入"""
        size = self.size
        region_size = self.sqrt_n
        
        # 检查行和列
        if num in grid[row] or num in [grid[i][col] for i in range(size)]:
            return False
            
        # 检查子区域
        start_row, start_col = row - row%region_size, col - col%region_size
        for i in range(region_size):
            for j in range(region_size):
                if grid[start_row+i][start_col+j] == num:
                    return False
        return True

    def _dig_holes(self, grid: List[List[int]], dig_prob: float) -> List[List[int]]:
        """挖洞生成谜题（保证至少有一个解）"""
        size = self.size
        for i in range(size):
            for j in range(size):
                if random.random() < dig_prob:
                    grid[i][j] = 0
        return grid
