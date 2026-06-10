import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class SkyscrapersRewardCalculator(BaseRewardCalculator):
    """Skyscrapers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        solution_str = matches[-1].strip()
        solution = []
        for line in solution_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if not all(part.isdigit() for part in parts):
                return None
            solution.append([int(part) for part in parts])
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        n = identity['n']
        clues = identity['clues']
        
        if len(solution) != n or any(len(row) != n for row in solution):
            return False
        
        for row in solution:
            if sorted(row) != list(range(1, n+1)):
                return False
        
        for col in range(n):
            column = [solution[row][col] for row in range(n)]
            if sorted(column) != list(range(1, n+1)):
                return False
        
        for i in range(n):
            row = solution[i]
            if (cls.compute_view(row) != clues['left'][i] or
                cls.compute_view(row[::-1]) != clues['right'][i]):
                return False
        
        for j in range(n):
            col = [solution[i][j] for i in range(n)]
            if (cls.compute_view(col) != clues['top'][j] or
                cls.compute_view(col[::-1]) != clues['bottom'][j]):
                return False
        
        return True
    
    # 其他额外方法

