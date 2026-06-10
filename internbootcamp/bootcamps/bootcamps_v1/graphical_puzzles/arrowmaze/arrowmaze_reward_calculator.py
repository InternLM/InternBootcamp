import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.arrowmaze.lib.maze_generator import generate_arrow_maze




class ArrowmazeRewardCalculator(BaseRewardCalculator):
    """Arrowmaze奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """
        Extract the output from the solution.
        
        Args:
            output: Model output to be processed.
        
        Returns:
            The processed output.
        """
        pattern = pattern = r'```json\s*([\s\S]*?)\s*```'
        matches = re.findall(pattern, output)
        # Final-answer:{'A': [(3, 1)],
        # 'B': [(1, 4)],
        # 'C': [(2, 3)],
        # 'D': [(5, 2)],
        # 'E': [(4, 5)]}
        if matches:
            # 获取 JSON 字符串
            json_str = matches[-1]
            # print('match?', json_str)
            # print('solution generated? first lines', output[:200])
            # print('solution generated? last lines', output[-200:])
            # 替换单引号为双引号，将元组表示改为列表表示
            json_str = json_str.replace("'", '"').replace("(", "[").replace(")", "]")
            try:
                # 解析 JSON 字符串为 Python 字典
                result_dict = json.loads(json_str)
                return result_dict
            except json.JSONDecodeError as e:
                return json_str
        else:
            return None
    
    @staticmethod 
    def _verify_correction(solution,identity:dict)->bool:
        """
        Validate whether a candidate_path in puzzle's format (e.g. "[[1 0 0,0 0 0,0 0 2]]")
        is a correct solution to the arrow maze.

        Parameters
        ----------
        grid : list[list[str]]
            A 2D grid of arrow symbols or '○'.
            Example:
            [
            ['→', '↙', '↓'],
            ['↖', '↓', '↙'],
            ['↑', '←', '○'],
            ]
        start_position : (int, int)
            (row, col) of the starting cell.
        answer : list
            The proposed solution in the format "[[...]]"
            0 => not on path
            1 => first visited cell
            2 => second visited cell
            etc.

        Returns
        -------
        bool
            True if the path is valid, False otherwise.
        """
        if not 'input_grid' in identity:
            raise ValueError("input_grid is not in identity")
        else:
            input_grid = identity['input_grid']
        
        if not 'start_position' in identity:
            start_position = (0, 0)
        else:
            start_position = tuple(identity['start_position'])
        input_grid = json.loads(input_grid) if type(input_grid) == str else input_grid
        candidate_grid = json.loads(solution) if type(solution) == str else solution
        # Directions dictionary: maps arrow symbol -> (dr, dc)
        DIRECTIONS = {
            '↑':  (-1,  0),
            '↓':  ( 1,  0),
            '←':  ( 0, -1),
            '→':  ( 0,  1),
            '↖':  (-1, -1),
            '↗':  (-1,  1),
            '↙':  ( 1, -1),
            '↘':  ( 1,  1),
        }

        rows = len(input_grid)
        cols = len(input_grid[0]) if rows > 0 else 0

        def in_bounds(r, c):
            return 0 <= r < rows and 0 <= c < cols

        
        
        # candidate_grid = answer

        # Sanity check: the candidate_grid should match the same dimensions as 'grid'
        if len(candidate_grid) != rows:
            return False
        for row_vals in candidate_grid:
            if len(row_vals) != cols:
                return False
        
        # 2. Extract the labeled cells: (label, (row, col))
        #    We only care about label > 0
        labeled_cells = []
        for r in range(rows):
            for c in range(cols):
                label = candidate_grid[r][c]
                if label > 0:
                    labeled_cells.append((label, (r, c)))
        
        # If no labeled cells, invalid
        if not labeled_cells:
            return False
        
        # 3. Sort by label ascending
        labeled_cells.sort(key=lambda x: x[0])  # sort by label number
        # This gives us an ordered path: [ (1, (r1,c1)), (2, (r2,c2)), ... ]

        # 4. The path in terms of coordinates:
        path = [cell_coord for _, cell_coord in labeled_cells]

        # 5. Check that label "1" is at start_position
        if path[0] != start_position:
            return False

        # 6. Validate each consecutive step in path
        for i in range(len(path) - 1):
            (r1, c1) = path[i]
            (r2, c2) = path[i + 1]

            if not in_bounds(r1, c1) or not in_bounds(r2, c2):
                return False

            # If the current cell is the end symbol '○' but we still have more steps, invalid
            if input_grid[r1][c1] == '○':
                return False

            # Arrow in the current cell:
            arrow_symbol = input_grid[r1][c1]
            if arrow_symbol not in DIRECTIONS:
                return False  # not an arrow and not the end symbol

            (dr, dc) = DIRECTIONS[arrow_symbol]
            delta_r = r2 - r1
            delta_c = c2 - c1

            # Must move in a positive integer multiple of (dr, dc).
            if dr == 0 and dc == 0:
                return False  # shouldn't happen with valid arrows

            # Horizontal or vertical
            if dr == 0:
                # vertical movement is zero => must move horizontally
                # check we didn't move in row, must move in col
                if delta_r != 0:
                    return False
                # direction must match sign of dc
                if dc > 0 and delta_c <= 0:
                    return False
                if dc < 0 and delta_c >= 0:
                    return False
            elif dc == 0:
                # horizontal movement is zero => must move in row
                if delta_c != 0:
                    return False
                if dr > 0 and delta_r <= 0:
                    return False
                if dr < 0 and delta_r >= 0:
                    return False
            else:
                # diagonal
                if delta_r == 0 or delta_c == 0:
                    return False  # can't be diagonal if one is zero
                if (dr > 0 and delta_r <= 0) or (dr < 0 and delta_r >= 0):
                    return False
                if (dc > 0 and delta_c <= 0) or (dc < 0 and delta_c >= 0):
                    return False
                # check integer multiples
                if (delta_r % dr) != 0 or (delta_c % dc) != 0:
                    return False
                factor_r = delta_r // dr
                factor_c = delta_c // dc
                if factor_r != factor_c or factor_r <= 0:
                    return False

        # 7. Check last labeled cell is the '○' cell
        last_r, last_c = path[-1]
        if not in_bounds(last_r, last_c):
            return False
        if input_grid[last_r][last_c] != '○':
            return False

        # If all checks pass, it's a valid solution
        return True
    
    # 其他额外方法

