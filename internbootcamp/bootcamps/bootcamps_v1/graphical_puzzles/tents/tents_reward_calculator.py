import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Tuple




class TentsRewardCalculator(BaseRewardCalculator):
    """Tents奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> List[Tuple[int, int]]:
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            last_match = matches[-1].strip()
            solution = ast.literal_eval(last_match)
            if isinstance(solution, list) and all(isinstance(t, tuple) and len(t)==2 for t in solution):
                return solution
        except:
            pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity) -> bool:
        if not isinstance(solution, list):
            return False
        
        try:
            user_coords = [(x-1, y-1) for (x, y) in solution]
        except:
            return False
        
        if len(user_coords) != len(set(user_coords)):
            return False
        
        grid = identity['grid']
        rows, cols = len(grid), len(grid[0])
        row_clues = identity['row_clues']
        col_clues = identity['col_clues']
        
        # Coordinate validation
        for x, y in user_coords:
            if x < 0 or y < 0 or x >= rows or y >= cols:
                return False
            if grid[x][y] == 1:
                return False
        
        # Tent adjacency check
        tents = set(user_coords)
        for (x1, y1) in tents:
            for (x2, y2) in tents:
                if (x1, y1) == (x2, y2):
                    continue
                if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
                    return False
        
        # Tree-tent mapping validation
        tree_counts = {(i,j):0 for i in range(rows) for j in range(cols) if grid[i][j]}
        for x, y in tents:
            adjacent_tree = False
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < rows and 0 <= ny < cols:
                    if grid[nx][ny]:
                        adjacent_tree = True
                        tree_counts[(nx, ny)] += 1
            if not adjacent_tree:
                return False
        
        if any(cnt != 1 for cnt in tree_counts.values()):
            return False
        
        # Clues validation
        actual_rows = [0]*rows
        actual_cols = [0]*cols
        for x, y in tents:
            actual_rows[x] += 1
            actual_cols[y] += 1
        return actual_rows == row_clues and actual_cols == col_clues
    
    # 其他额外方法

