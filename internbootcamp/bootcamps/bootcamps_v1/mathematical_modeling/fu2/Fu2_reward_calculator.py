import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def cw(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (c[0] - b[0]) * (b[1] - a[1]) < 0

def compute_expected(transformed_points):
    if not transformed_points:
        return 0
    transformed_points.sort()
    n = len(transformed_points)
    hull = [transformed_points[0]]
    for i in range(1, n):
        current_point = transformed_points[i]
        if cw(transformed_points[0], current_point, transformed_points[-1]) or (i == n - 1):
            while len(hull) >= 2 and not cw(hull[-2], hull[-1], current_point):
                hull.pop()
            hull.append(current_point)
    res = 0
    for i in range(1, len(hull)):
        if hull[i][0] != hull[i-1][0]:
            res += 1
    return res


class Fu2RewardCalculator(BaseRewardCalculator):
    """Fu2奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        answers = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(answers[-1]) if answers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity["expected"]
    
    # 其他额外方法

