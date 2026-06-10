import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CcycleRewardCalculator(BaseRewardCalculator):
    """Ccycle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip()
        if answer == '-1':
            return -1
        else:
            parts = answer.split()
            if len(parts) != 3:
                return None
            try:
                a1, a2, a3 = map(int, parts)
                return (a1, a2, a3)
            except:
                return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution == -1:
            return not identity['has_cycle']
        else:
            a1, a2, a3 = solution
            a1 -= 1  # 转换为0-based索引
            a2 -= 1
            a3 -= 1
            adj_matrix = identity['adj_matrix']
            # 检查a1→a2
            if a1 < 0 or a1 >= len(adj_matrix) or a2 < 0 or a2 >= len(adj_matrix[a1]) or adj_matrix[a1][a2] != '1':
                return False
            # 检查a2→a3
            if a2 < 0 or a2 >= len(adj_matrix) or a3 < 0 or a3 >= len(adj_matrix[a2]) or adj_matrix[a2][a3] != '1':
                return False
            # 检查a3→a1
            if a3 < 0 or a3 >= len(adj_matrix) or a1 < 0 or a1 >= len(adj_matrix[a3]) or adj_matrix[a3][a1] != '1':
                return False
            return True
    
    # 其他额外方法

