import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Tuple




class TentsInstructionGenerator(BaseInstructionGenerator):
    """Tents Bootcamp指令生成器"""
    
    def __init__(self, rows=5, cols=5):
        """
        初始化Tents指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = rows
        self.cols = cols
    
    def case_generator(self) -> dict:
        while True:
            # Generate valid tent positions
            tent_positions = self._generate_tent_positions()
            if not tent_positions:
                continue
            
            # Generate corresponding tree positions
            grid, tree_positions = self._place_trees(tent_positions)
            if not grid:
                continue
            
            # Verify tree-tent mapping
            if not self._validate_tree_tents(grid, tent_positions, tree_positions):
                continue
            
            # Generate row and column clues
            row_clues = [sum(1 for x, y in tent_positions if x == i) for i in range(self.rows)]
            col_clues = [sum(1 for x, y in tent_positions if y == j) for j in range(self.cols)]
            
            # Convert grid to 0/1 matrix
            grid_matrix = [[1 if (i, j) in tree_positions else 0 for j in range(self.cols)] 
                          for i in range(self.rows)]
            
            return {
                'grid': grid_matrix,
                'row_clues': row_clues,
                'col_clues': col_clues,
                'solution': tent_positions
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid = question_case['grid']
        row_clues = question_case['row_clues']
        col_clues = question_case['col_clues']
        
        # Build grid visualization
        grid_str = "   " + " ".join(str(i+1) for i in range(len(grid[0]))) + "\n"
        for idx, row in enumerate(grid):
            cells = ["T" if cell else "." for cell in row]
            grid_str += f"{idx+1:2} {' '.join(cells)} {row_clues[idx]}\n"
        grid_str += f"   {' '.join(map(str, col_clues))}"
        
        return f"""你是一个帐篷谜题专家，请根据以下规则布置帐篷：

规则：
1. 每个帐篷必须与一棵树正交相邻
2. 每棵树必须对应恰好一个帐篷
3. 帐篷之间不能相邻（包括对角线）
4. 行列数字表示对应行/列的帐篷数量

谜题网格（行末和底部为数量提示）：
{grid_str}

请将答案用[answer]标签包裹，例如：[answer] [(1,2), (3,4)] [/answer]。坐标采用(行号,列号)格式，从1开始计数。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_tent_positions(self) -> List[Tuple[int, int]]:
        available = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        tents = []
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        random.shuffle(positions)

        for x, y in positions:
            if available[x][y]:
                tents.append((x, y))
                # Mark surrounding cells as unavailable
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            available[nx][ny] = False
        return tents

    def _place_trees(self, tent_positions) -> Tuple[List[List[int]], List[Tuple[int, int]]]:
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        tree_positions = []

        for x, y in tent_positions:
            directions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            random.shuffle(directions)
            placed = False
            for dx, dy in directions:
                if 0 <= dx < self.rows and 0 <= dy < self.cols:
                    if grid[dx][dy] == 0 and (dx, dy) not in tent_positions:
                        grid[dx][dy] = 1
                        tree_positions.append((dx, dy))
                        placed = True
                        break
            if not placed:
                return None, None
        return grid, tree_positions

    def _validate_tree_tents(self, grid, tents, trees) -> bool:
        # Check tent adjacency
        for i in range(len(tents)):
            for j in range(i+1, len(tents)):
                x1, y1 = tents[i]
                x2, y2 = tents[j]
                if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
                    return False

        # Check tree-tent mapping
        tree_counts = {(i,j):0 for i in range(self.rows) for j in range(self.cols) if grid[i][j]}
        for x, y in tents:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if grid[nx][ny]:
                        tree_counts[(nx, ny)] += 1
        return all(c == 1 for c in tree_counts.values())
