import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from itertools import combinations




class CpromocodeswithmistakesRewardCalculator(BaseRewardCalculator):
    """Cpromocodeswithmistakes奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """答案提取方法"""
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """验证逻辑优化"""
        codes = identity['promocodes']
        n = identity['n']
        
        if n == 1:
            return solution == 6
        
        min_k = 6  # 初始化为最大可能值
        for a, b in combinations(codes, 2):
            diff = sum(1 for x, y in zip(a, b) if x != y)
            current_k = (diff - 1) // 2
            min_k = min(min_k, current_k)
            if min_k == 0:  # 提前终止条件
                break
        return solution == max(min_k, 0)
    
    # 其他额外方法

