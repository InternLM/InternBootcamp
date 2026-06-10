import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class NonogramsRewardCalculator(BaseRewardCalculator):
    """Nonograms奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        grid_str = matches[-1].strip()
        solution = []
        for line in grid_str.split('\n'):
            line = line.strip()
            if not line:
                continue
            solution.append([c.upper() == 'X' for c in line if not c.isspace() or c == '.'])
        return solution
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # Validate grid dimensions
        if len(solution) != len(identity['rows']):
            return False
        if any(len(row) != len(identity['columns']) for row in solution):
            return False

        # Check row clues
        for i, row in enumerate(solution):
            if cls._get_clues(row) != identity['rows'][i]:
                return False

        # Check column clues
        for j in range(len(identity['columns'])):
            col = [solution[i][j] for i in range(len(solution))]
            if cls._get_clues(col) != identity['columns'][j]:
                return False

        return True
    
    # 其他额外方法

