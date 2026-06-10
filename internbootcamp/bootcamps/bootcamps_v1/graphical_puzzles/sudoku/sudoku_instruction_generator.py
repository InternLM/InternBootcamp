import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import random
from typing import List
from typing import Optional




class SudokuInstructionGenerator(BaseInstructionGenerator):
    """Sudoku Bootcamp指令生成器"""
    
    def __init__(self, size: int = 9):
        """
        初始化Sudoku指令生成器
        
        Args:
            size: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
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
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
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
