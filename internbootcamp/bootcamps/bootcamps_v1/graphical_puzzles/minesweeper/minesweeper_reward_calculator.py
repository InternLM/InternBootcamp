import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import ast




class MinesweeperRewardCalculator(BaseRewardCalculator):
    """Minesweeper奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_match)
            if (isinstance(solution, list) and 
                all(isinstance(coord, list) and len(coord) == 2 for coord in solution)):
                return solution
            return None
        except (SyntaxError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list):
            return False
        try:
            solution_set = {tuple(coord) for coord in solution}
        except TypeError:
            return False
        mines = identity.get('mines', [])
        mines_set = {tuple(mine) for mine in mines}
        if len(solution_set) != len(mines_set):
            return False
        rows, cols = identity['rows'], identity['cols']
        for (r, c) in solution_set:
            if not (0 <= r < rows and 0 <= c < cols):
                return False
        return solution_set == mines_set
    
    # 其他额外方法

