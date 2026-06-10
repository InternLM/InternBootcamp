import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class KorpuzzleskyscrapersRewardCalculator(BaseRewardCalculator):
    """Korpuzzleskyscrapers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            # Handle multi-line formatting
            cleaned = ' '.join(last_match.splitlines()).replace(' , ', ', ').replace(', ', ',')
            rows = [r.strip() for r in cleaned.split(',')]
            solution = []
            for row in rows:
                solution.append([int(num) for num in row.split()])
            return solution
        except Exception as e:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        # Validate solution structure
        if not (isinstance(solution, list) and len(solution) == n and all(len(row) == n for row in solution)):
            return False
        
        # Verify Latin square properties
        expected = list(range(1, n+1))
        for row in solution:
            if sorted(row) != expected:
                return False
        for col in range(n):
            column = [solution[row][col] for row in range(n)]
            if sorted(column) != expected:
                return False
        
        # Verify visibility constraints
        for i in range(n):
            row = solution[i]
            if cls.count_visible(row) != identity['left'][i]:
                return False
            if cls.count_visible(reversed(row)) != identity['right'][i]:
                return False
        
        for j in range(n):
            column = [solution[i][j] for i in range(n)]
            if cls.count_visible(column) != identity['top'][j]:
                return False
            if cls.count_visible(reversed(column)) != identity['bottom'][j]:
                return False
        
        return True
    
    # 其他额外方法

