import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from math import gcd




class AvasyaandtriangleRewardCalculator(BaseRewardCalculator):
    """Avasyaandtriangle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.DOTALL | re.IGNORECASE)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        lines = [line.strip() for line in last_answer.split('\n') if line.strip()]
        if not lines:
            return None
        if lines[0].upper() == 'NO':
            return 'NO'
        elif lines[0].upper() == 'YES' and len(lines) == 4:
            points = []
            for line in lines[1:4]:
                parts = line.split()
                if len(parts) != 2:
                    return None
                try:
                    x, y = int(parts[0]), int(parts[1])
                    points.append((x, y))
                except ValueError:
                    return None
            return points
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        m = identity['m']
        k = identity['k']
        solvable = identity['solvable']

        if not solvable:
            return isinstance(solution, str) and solution.upper() == 'NO'
        if solution == 'NO':
            return False
        if not isinstance(solution, list) or len(solution) != 3:
            return False

        for x, y in solution:
            if not (0 <= x <= n and 0 <= y <= m):
                return False

        x1, y1 = solution[0]
        x2, y2 = solution[1]
        x3, y3 = solution[2]
        area_twice = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))
        expected_twice_area = (2 * n * m) // k
        return area_twice == expected_twice_area
    
    # 其他额外方法

