import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import bisect

# === 源文件中的全局函数 ===

def solve(n, m, obstacles):
    if n == 0 or m == 0:
        return "No"
    
    obstacles_x = [[-1, m] for _ in range(n)]
    obstacles_y = [[-1, n] for _ in range(m)]
    
    for x, y in obstacles:
        x0 = x - 1
        y0 = y - 1
        bisect.insort(obstacles_x[x0], y0)
        bisect.insort(obstacles_y[y0], x0)

    for row in obstacles_x:
        row.sort()
    for col in obstacles_y:
        col.sort()

    flag = 1
    traversed = 0
    turn = 1
    curr_x, curr_y = 0, -1
    lower_x, upper_x = 0, n
    lower_y, upper_y = -1, m

    while flag == 1:
        flag = 0
        if turn == 1:
            idx = bisect.bisect_right(obstacles_x[curr_x], curr_y)
            next_y = min(upper_y-1, obstacles_x[curr_x][idx]-1)
            if next_y > curr_y:
                traversed += next_y - curr_y
                flag = 1
                turn = 2
                curr_y, upper_y = next_y, next_y
        elif turn == 2:
            idx = bisect.bisect_right(obstacles_y[curr_y], curr_x)
            next_x = min(upper_x-1, obstacles_y[curr_y][idx]-1)
            if next_x > curr_x:
                traversed += next_x - curr_x
                flag = 1
                turn = 3
                curr_x, upper_x = next_x, next_x
        elif turn == 3:
            idx = bisect.bisect_right(obstacles_x[curr_x], curr_y) - 1
            next_y = max(lower_y+1, obstacles_x[curr_x][idx]+1)
            if next_y < curr_y:
                traversed += curr_y - next_y
                flag = 1
                turn = 4
                curr_y, lower_y = next_y, next_y
        else:
            idx = bisect.bisect_left(obstacles_y[curr_y], curr_x) - 1
            next_x = max(lower_x+1, obstacles_y[curr_y][idx]+1)
            if next_x < curr_x:
                traversed += curr_x - next_x
                flag = 1
                turn = 1
                curr_x, lower_x = next_x, next_x

    total_cells = n * m - len(obstacles)
    return "Yes" if traversed == total_cells else "No"


class DaliceandthedollRewardCalculator(BaseRewardCalculator):
    """Daliceandthedoll奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*(Yes|No)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1].capitalize() if matches else None
    
    @classmethod
    def _verify_correction(cls, sol, case):
        correct = solve(case['n'], case['m'], case['obstacles'])
        return sol.lower() == correct.lower()
    
    # 其他额外方法

