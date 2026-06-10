import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
from collections import defaultdict




class CdominoesRewardCalculator(BaseRewardCalculator):
    """Cdominoes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answers = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answers: return None
        matrix = []
        for line in answers[-1].strip().split('\n'):
            if line.strip():
                matrix.append(line.strip().split())
        return matrix if len(matrix) == 0 or len(matrix[0]) == matrix[0].__len__() else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 尺寸验证
        if len(solution) != identity['n']: return False
        if any(len(row)!=identity['m'] for row in solution): return False
        
        # 多米诺来源验证
        orig = defaultdict(int)
        for row in identity['input_matrix']:
            for d in row:
                key = d if d in ['00','11'] else '01'
                orig[key] += 1
                
        sol = defaultdict(int)
        for row in solution:
            for d in row:
                key = d if d in ['00','11'] else '01'
                sol[key] += 1
        if orig != sol: return False
        
        # 列和验证
        columns = [0]*(2*identity['m'])
        for row in solution:
            for i, domino in enumerate(row):
                columns[2*i] += int(domino[0])
                columns[2*i+1] += int(domino[1])
        return max(columns) == identity['optimal_max']
    
    # 其他额外方法

