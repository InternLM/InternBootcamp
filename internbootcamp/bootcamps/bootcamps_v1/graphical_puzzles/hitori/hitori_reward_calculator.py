import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import ast




class HitoriRewardCalculator(BaseRewardCalculator):
    """Hitori奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            result = ast.literal_eval(matches[-1].strip())
            if isinstance(result, list) and all(isinstance(cell, tuple) and len(cell) == 2 for cell in result):
                return result
        except:
            pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, list):
            return False
        grid = identity["grid"]
        size = len(grid)
        shaded = set(solution)
        
        if len(shaded) != len(solution):
            return False
        
        for i, j in shaded:
            if not (0 <= i < size and 0 <= j < size):
                return False
            for di, dj in [(-1,0), (1,0), (0,-1), (0,1)]:
                if (i + di, j + dj) in shaded:
                    return False
        
        unshaded = [(i, j) for i in range(size) for j in range(size) if (i, j) not in shaded]
        for i in range(size):
            row = [grid[r][c] for r, c in unshaded if r == i]
            if len(row) != len(set(row)):
                return False
            col = [grid[r][c] for r, c in unshaded if c == i]
            if len(col) != len(set(col)):
                return False
        
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
                if (ni, nj) in unshaded and (ni, nj) not in visited:
                    queue.append((ni, nj))
        return len(visited) == len(unshaded)
    
    # 其他额外方法

