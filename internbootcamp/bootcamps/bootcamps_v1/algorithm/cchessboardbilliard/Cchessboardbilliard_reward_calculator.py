import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CchessboardbilliardRewardCalculator(BaseRewardCalculator):
    """Cchessboardbilliard奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """强化答案提取鲁棒性"""
        matches = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            output.replace(' ', '').lower(),
            re.DOTALL
        )
        if not matches:
            return None
        last_val = matches[-1].strip()
        try:
            return int(round(float(last_val)))  # 兼容浮点格式
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """完全遵循参考算法逻辑的验证"""
        try:
            # 参数交换逻辑修正
            n, m = identity['n'], identity['m']
            if n < m:
                n, m = m, n
            
            # 初始化参数
            d = [True] * n
            transformed_m = 2 * m - 2
            nn = 2 * n - 2
            result = 0
            
            # 完全复制参考算法逻辑
            for i in range(n):
                if not d[i]:
                    continue
                result += 1
                j = k = i
                while True:
                    d[k] = False
                    j += transformed_m
                    if j >= nn:
                        j -= nn
                    if j == i:
                        break
                    k = j if j < n else nn - j
            
            return solution == result
        except Exception as e:
            return False
    
    # 其他额外方法

