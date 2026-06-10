import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CvladikandfractionsRewardCalculator(BaseRewardCalculator):
    """Cvladikandfractions奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        if last_answer == '-1':
            return -1
        parts = last_answer.split()
        if len(parts) != 3:
            return None
        try:
            x, y, z = map(int, parts)
            return (x, y, z)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity["n"]
        if n == 1:
            return solution == -1  # n=1时只有-1正确
        else:
            # 其他n必须返回有效三元组
            if solution == -1:
                return False  # n≥2时不接受-1
            if not isinstance(solution, tuple) or len(solution) != 3:
                return False
            x, y, z = solution
            if x <= 0 or y <= 0 or z <= 0:
                return False
            if x > 1e9 or y > 1e9 or z > 1e9:
                return False
            if x == y or x == z or y == z:
                return False
            # 关键数学验证：n(xy + yz + zx) == 2xyz
            left = n * (x * y + y * z + z * x)
            right = 2 * x * y * z
            return left == right
    
    # 其他额外方法

