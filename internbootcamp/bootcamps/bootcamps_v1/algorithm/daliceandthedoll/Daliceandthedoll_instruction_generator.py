import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class DaliceandthedollInstructionGenerator(BaseInstructionGenerator):
    """Daliceandthedoll Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, min_m=1, max_m=5):
        """
        初始化Daliceandthedoll指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        m = random.randint(self.min_m, self.max_m)
        max_k = n*m -1
        k = random.randint(0, max_k) if max_k > 0 else 0
        
        available = [(x,y) for x in range(1,n+1) for y in range(1,m+1) if (x,y) != (1,1)]
        obstacles = random.sample(available, k) if k else []
        
        return {
            'n': n,
            'm': m,
            'k': k,
            'obstacles': obstacles
        }
    
    @staticmethod
    def prompt_func(case):
        input_str = f"{case['n']} {case['m']} {case['k']}"
        for x,y in case['obstacles']:
            input_str += f"\n{x} {y}"
        
        return f"""Alice的玩偶走迷宫问题。迷宫大小为{case['n']}行×{case['m']}列，有{case['k']}个障碍物。玩偶从(1,1)出发，初始向右，每次可直行或原地右转一次。要求遍历所有无障碍格且不重复。是否可行？

输入格式：
{input_str}

请分析路径可能性，并用[answer]标签包裹答案（Yes/No）。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

