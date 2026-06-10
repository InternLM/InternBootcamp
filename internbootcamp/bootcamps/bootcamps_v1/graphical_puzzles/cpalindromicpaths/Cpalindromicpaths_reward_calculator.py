import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random




class CpalindromicpathsRewardCalculator(BaseRewardCalculator):
    """Cpalindromicpaths奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip()
        rows = answer.split('\n')
        rows = [row.strip() for row in rows if row.strip() != '']
        for row in rows:
            if not all(c in '01' for c in row):
                return None
        return rows
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        expected_grid = identity['grid']
        
        if len(solution) != n:
            return False
        for row in solution:
            if len(row) != n:
                return False
        
        actual_grid = []
        for row in solution:
            actual_grid.append([int(c) for c in row])
        
        for i in range(n):
            for j in range(n):
                if actual_grid[i][j] != expected_grid[i][j]:
                    return False
        return True
    
    # 其他额外方法

