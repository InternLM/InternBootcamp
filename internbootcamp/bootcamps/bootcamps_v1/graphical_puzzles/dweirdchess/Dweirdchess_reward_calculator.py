import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class DweirdchessRewardCalculator(BaseRewardCalculator):
    """Dweirdchess奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = re.compile(r'\[answer\](.*?)\[/answer\]', re.DOTALL)
        matches = pattern.findall(output)
        if not matches:
            return None
        answer_content = matches[-1].strip()
        lines = [line.strip() for line in answer_content.split('\n') if line.strip()]

        if not lines:
            return None
        first_line = lines[0].upper()
        if first_line == 'NO':
            return ['NO']
        elif first_line == 'YES':
            if len(lines) < 2:
                return None
            matrix = lines[1:]
            size = len(matrix)
            if (size + 1) % 2 != 0:
                return None
            n = (size + 1) // 2
            if any(len(row) != size for row in matrix):
                return None
            if matrix[n-1][n-1] != 'o':
                return None
            for row in matrix:
                if not all(c in {'x', '.', 'o'} for c in row):
                    return None
            return matrix
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution == ['NO']:
            return False

        n = identity['n']
        input_grid = identity['grid']

        try:
            size = len(solution)
            if size != 2 * n - 1:
                return False
            for row in solution:
                if len(row) != size:
                    return False
            if solution[n-1][n-1] != 'o':
                return False

            move_vectors = []
            for i in range(size):
                for j in range(size):
                    if solution[i][j] == 'x':
                        dx = j - (n-1)
                        dy = i - (n-1)
                        move_vectors.append((dx, dy))

            temp_grid = [list(row) for row in input_grid]
            o_positions = [(x, y) for y in range(n) for x in range(n) if input_grid[y][x] == 'o']

            for x, y in o_positions:
                for dx, dy in move_vectors:
                    tx = x + dx
                    ty = y + dy
                    if 0 <= tx < n and 0 <= ty < n:
                        if temp_grid[ty][tx] == 'x':
                            temp_grid[ty][tx] = '.'

            for row in temp_grid:
                if 'x' in row:
                    return False
            return True
        except:
            return False
    
    # 其他额外方法

