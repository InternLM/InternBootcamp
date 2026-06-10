import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class DrearrangeRewardCalculator(BaseRewardCalculator):
    """Drearrange奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        return matches[-1].strip() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution == '-1':
            return False  # 原案例确保存在解
        
        try:
            # 转换并验证解矩阵格式
            matrix = []
            for line in solution.split('\n'):
                if not line.strip():
                    continue
                row = list(map(int, line.strip().split()))
                matrix.append(row)
            
            return cls._validate_solution(matrix, identity['matrix'])
        except:
            return False
    
    # 其他额外方法

