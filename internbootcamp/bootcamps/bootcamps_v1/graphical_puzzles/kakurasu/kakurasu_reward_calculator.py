import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
import ast




class KakurasuRewardCalculator(BaseRewardCalculator):
    """Kakurasu奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_match)
            return solution
        except (SyntaxError, ValueError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        row_targets = identity['row_targets']
        col_targets = identity['col_targets']
        
        # 验证答案结构
        if not isinstance(solution, list) or len(solution) != n:
            return False
        for row in solution:
            if not isinstance(row, list) or len(row) != n:
                return False
            for cell in row:
                if cell not in (0, 1):
                    return False
        
        # 验证行约束
        for i in range(n):
            row_sum = sum((j + 1) * cell for j, cell in enumerate(solution[i]))
            if row_sum != row_targets[i]:
                return False
        
        # 验证列约束
        for j in range(n):
            col_sum = sum((i + 1) * solution[i][j] for i in range(n))
            if col_sum != col_targets[j]:
                return False
        
        return True
    
    # 其他额外方法

