import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from math import hypot
import bisect
import random
import re




class DbuildingbridgeRewardCalculator(BaseRewardCalculator):
    """Dbuildingbridge奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 支持多种分隔符和首尾空格
        pattern = r'\[answer\]\s*(\d+)[\s,;]+(\d+)\s*\[/answer\]'
        matches = re.findall(pattern, output, re.IGNORECASE)
        if matches:
            last_match = matches[-1]
            try:
                return (int(last_match[0]), int(last_match[1]))
            except ValueError:
                pass
        return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        if not solution or len(solution) != 2:
            return False
        
        west_idx, east_idx = solution
        west_idx -= 1  # 转换为0-based
        east_idx -= 1
        
        # 索引有效性检查
        if not (0 <= west_idx < case['n'] and 0 <= east_idx < case['m']):
            return False
        
        # 计算实际路径
        a = case['a']
        b = case['b']
        ai_y = case['west_ys'][west_idx]
        bj_y = case['east_ys'][east_idx]
        lj = case['l_list'][east_idx]
        
        total = (
            hypot(a, ai_y) +
            hypot(b - a, bj_y - ai_y) +
            lj
        )
        
        # 允许的误差范围
        return abs(total - case['min_total']) <= 1e-6 * (1 + abs(case['min_total']))
    
    # 其他额外方法

