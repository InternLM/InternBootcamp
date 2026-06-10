import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from itertools import product




class KorpuzzleminesweeperRewardCalculator(BaseRewardCalculator):
    """Korpuzzleminesweeper奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        pattern = r'\[\[((?:[^[\]]|\[.*?\])*?)\]\]'  # 处理嵌套括号
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        
        last_match = matches[-1].replace('\n', ' ').replace('\t', ' ')
        rows = [r.strip() for r in last_match.split(',')]
        solution = []
        for row in rows:
            cells = list(filter(None, re.split(r'[\s,]+', row)))
            if cells:
                solution.append(cells)
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            puzzle_grid = identity['grid']
            full_grid = identity['full_grid']
            mines = set(map(tuple, identity['mines']))
            
            # 结构校验
            if len(solution) != len(puzzle_grid):
                return False
            for r in range(len(puzzle_grid)):
                if len(solution[r]) != len(puzzle_grid[r]):
                    return False
            
            # 内容校验
            for r in range(len(puzzle_grid)):
                for c in range(len(puzzle_grid[r])):
                    puzzle_val = puzzle_grid[r][c]
                    ans_val = solution[r][c]
                    
                    if puzzle_val != 'X':  # 原始提示格必须保持一致
                        if ans_val != puzzle_val:
                            return False
                    else:  # X格需要验证地雷状态
                        is_mine = (r,c) in mines
                        if is_mine and ans_val != 'A':
                            return False
                        if not is_mine and ans_val != 'X':
                            return False
            return True
        except Exception as e:
            print(f"Verification error: {e}")
            return False
    
    # 其他额外方法

