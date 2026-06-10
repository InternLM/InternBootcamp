import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import ast




class HitoriInstructionGenerator(BaseInstructionGenerator):
    """Hitori Bootcamp指令生成器"""
    
    def __init__(self, size=5, number_range=None):
        """
        初始化Hitori指令生成器
        
        Args:
            size: 参数描述
            number_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.size = size
        self.number_range = number_range if number_range else (1, size)
    
    def case_generator(self):
        size = self.size
        grid = self._generate_latin_square(size)
        shaded_cells = self._generate_valid_shaded_cells(size)
        
        for i, j in shaded_cells:
            unshaded_row = [(i, c) for c in range(size) if (i, c) not in shaded_cells and c != j]
            unshaded_col = [(r, j) for r in range(size) if (r, j) not in shaded_cells and r != i]
            if unshaded_row:
                sample_cell = random.choice(unshaded_row)
                grid[i][j] = grid[sample_cell[0]][sample_cell[1]]
            elif unshaded_col:
                sample_cell = random.choice(unshaded_col)
                grid[i][j] = grid[sample_cell[0]][sample_cell[1]]
        
        return {"grid": grid}
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case["grid"]
        grid_str = "\n".join([" ".join(map(str, row)) for row in grid])
        return f"""你是一名Hitori谜题专家，请根据以下规则解决谜题：

规则：
1. 每行每列未涂黑数字必须唯一。
2. 涂黑单元格不能相邻（上下左右）。
3. 所有未涂黑单元格必须连通。

题目网格：
{grid_str}

请将答案的单元格坐标列表（从0开始）放在[answer]和[/answer]之间，例如：[answer][(0,1), (2,3)][/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_shaded_cells(self, size):
        shaded = set()
        candidates = [(i, j) for i in range(size) for j in range(size)]
        random.shuffle(candidates)

        for cell in candidates:
            i, j = cell
            adjacent = any((i + di, j + dj) in shaded for di, dj in [(-1,0), (1,0), (0,-1), (0,1)] if 0 <= i + di < size and 0 <= j + dj < size)
            if adjacent:
                continue
            shaded.add(cell)
            if not self._is_connected(size, shaded):
                shaded.remove(cell)
        return shaded

    def _is_connected(self, size, shaded):
        unshaded = [(i, j) for i in range(size) for j in range(size) if (i, j) not in shaded]
        if not unshaded:
            return False
        visited = set()
        queue = [unshaded[0]]
        while queue:
            cell = queue.pop(0)
            if cell in visited:
                continue
            visited.add(cell)
            i, j = cell
            for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                ni, nj = i + di, j + dj
                if 0 <= ni < size and 0 <= nj < size and (ni, nj) not in shaded and (ni, nj) not in visited:
                    queue.append((ni, nj))
        return len(visited) == len(unshaded)

    @staticmethod
    def _generate_latin_square(size):
        return [[(i + j) % size + 1 for j in range(size)] for i in range(size)]
