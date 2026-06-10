import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from ast import literal_eval




class KakuroRewardCalculator(BaseRewardCalculator):
    """Kakuro奖励计算器"""
    
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
    
    # 其他额外方法

