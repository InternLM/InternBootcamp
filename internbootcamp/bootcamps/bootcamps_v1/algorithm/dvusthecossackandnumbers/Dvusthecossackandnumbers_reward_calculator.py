import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import random
import re




class DvusthecossackandnumbersRewardCalculator(BaseRewardCalculator):
    """Dvusthecossackandnumbers奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 匹配最后一个[answer]块内的所有整数
        matches = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            # 允许换行符或空格分隔
            solution = list(map(int, re.split(r'[\n\s]+', last_match)))
            return solution
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 基础检查
        if not solution:
            return False
        if len(solution) != identity['n']:
            return False
        
        total = 0
        for b, a in zip(solution, identity['a_list']):
            floor = math.floor(a)
            ceil = math.ceil(a)
            
            # 检查是否有效舍入
            if b not in {floor, ceil}:
                return False
            
            # 检查数学约束
            if not (abs(a - b) < 1 - 1e-8):  # 处理浮点精度
                return False
            
            total += b
        
        return abs(total) < 1e-8  # 允许浮点误差
    
    # 其他额外方法

