import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import json
from random import randint
from random import choices
from random import shuffle
import random




class ClatinsquareRewardCalculator(BaseRewardCalculator):
    """Clatinsquare奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        matrix = []
        for line in last_match.split('\n'):
            line = line.strip()
            if not line:
                continue
            try:
                row = list(map(int, line.split()))
                matrix.append(row)
            except:
                return None
        return matrix if matrix and all(len(row) == len(matrix[0]) for row in matrix) else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'n' not in identity or 'matrix' not in identity or 'operations' not in identity:
            return False
        try:
            n = identity['n']
            expected = cls._compute_final(n, identity['matrix'], identity['operations'])
            # 检查每行的元素是否为1到n的排列
            for row in solution:
                if sorted(row) != list(range(1, n+1)):
                    return False
            return solution == expected
        except Exception as e:
            return False
    
    # 其他额外方法

