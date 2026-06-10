import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import math
from math import gcd




class CfadiandlcmRewardCalculator(BaseRewardCalculator):
    """Cfadiandlcm奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(\d+\s+\d+)\s*\[/answer\]', output)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        X = identity['X']
        
        # 解析答案
        try:
            a, b = map(int, solution.split())
            if a <= 0 or b <= 0:
                return False
        except:
            return False
        
        # 验证LCM正确性
        current_gcd = gcd(a, b)
        if a * b // current_gcd != X:
            return False
        
        # 计算最优解
        min_max = math.inf
        sqrt_x = int(math.sqrt(X))
        for i in range(1, sqrt_x + 1):
            if X % i == 0:
                j = X // i
                pair_gcd = gcd(i, j)
                candidate_max = max(i, j) * pair_gcd  # 关键优化点
                min_max = min(min_max, candidate_max)
        
        return max(a, b) == min_max
    
    # 其他额外方法

