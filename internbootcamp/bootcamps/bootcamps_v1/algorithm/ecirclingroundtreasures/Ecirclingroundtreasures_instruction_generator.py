import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class EcirclingroundtreasuresInstructionGenerator(BaseInstructionGenerator):
    """Ecirclingroundtreasures Bootcamp指令生成器"""
    
    def __init__(self, max_grid_size=8, max_objects=8):
        """
        初始化Ecirclingroundtreasures指令生成器
        
        Args:
            max_grid_size: 参数描述
            max_objects: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_grid_size = max_grid_size
        self.max_objects = max_objects
    
    def case_generator(self):
        for _ in range(100):
            n = random.randint(1, self.max_grid_size)
            m = random.randint(1, self.max_grid_size)
            grid = [['.' for _ in range(m)] for __ in range(n)]
            sx, sy = random.randint(0, n-1), random.randint(0, m-1)
            grid[sx][sy] = 'S'
            total_objects = random.randint(0, self.max_objects)
            num_treasures = random.randint(0, total_objects)
            num_bombs = total_objects - num_treasures
            available = []
            for i in range(n):
                for j in range(m):
                    if i != sx or j != sy:
                        available.append((i, j))
            if len(available) < total_objects:
                continue
            selected = random.sample(available, total_objects)
            for idx in range(num_treasures):
                i, j = selected[idx]
                grid[i][j] = str(idx + 1)
            for idx in range(num_treasures, total_objects):
                i, j = selected[idx]
                grid[i][j] = 'B'
            treasures_in_grid = [int(c) for row in grid for c in row if c.isdigit()]
            if num_treasures:
                sorted_t = sorted(treasures_in_grid)
                if sorted_t[0] != 1 or sorted_t[-1] != num_treasures or len(set(sorted_t)) != num_treasures:
                    continue
            treasure_values = [random.randint(-200, 200) for _ in range(num_treasures)]
            identity = {
                'n': n,
                'm': m,
                'grid': [''.join(row) for row in grid],
                'treasure_values': treasure_values,
                'correct_answer': None
            }
            try:
                identity['correct_answer'] = self.compute_max_profit(identity)
                if identity['correct_answer'] is not None:
                    return identity
            except:
                continue
        return {
            'n': 1,
            'm': 1,
            'grid': ['S'],
            'treasure_values': [],
            'correct_answer': 0
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        grid = question_case['grid']
        treasure_values = question_case['treasure_values']
        input_lines = [f"{n} {m}"] + grid + list(map(str, treasure_values))
        input_str = '\n'.join(input_lines)
        prompt = f"""You are a treasure hunter tasked with finding the maximum profit from a closed path on a map. The map is a grid where each cell can be an obstacle ('#'), a bomb ('B'), a treasure (digits '1'-'8'), your starting position ('S'), or empty ('.'). 

The goal is to construct a closed path starting and ending at 'S' that does not enclose any bombs. The profit is calculated as the sum of the values of treasures inside the path minus the number of moves in the path. 

Rules:
- The path must be a closed loop starting and ending at 'S'.
- Moves are allowed to adjacent cells (up, down, left, right).
- You cannot enter cells containing treasure, bombs, or obstacles.
- Bombs inside the enclosed area invalidate the path.
- Paths can self-intersect. Use the even-odd rule for determining enclosed cells.

Input:
{input_str}

Output a single integer: the maximum profit. If no valid path exists, output 0.

Please provide your answer within [answer] and [/answer], e.g., [answer]5[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_max_profit(identity):
        n, m = identity['n'], identity['m']
        grid = identity['grid']
        treasure_values = identity['treasure_values']
        sx = sy = None
        treasures = []
        bombs = []
        for i in range(n):
            for j in range(m):
                c = grid[i][j]
                if c == 'S':
                    sx, sy = i+1, j+1
                elif c.isdigit():
                    treasures.append((int(c), i+1, j+1))
                elif c == 'B':
                    bombs.append((i+1, j+1))
        treasures.sort()
        gx, gy, val = [], [], []
        for num, x, y in treasures:
            gx.append(x)
            gy.append(y)
            val.append(treasure_values[num-1])
        for x, y in bombs:
            gx.append(x)
            gy.append(y)
            val.append(-10000)
        m_objects = len(gx)
        tot = 1 << m_objects
        w = [0] * tot
        for mask in range(tot):
            total = 0
            for j in range(m_objects):
                if mask & (1 << j):
                    total += val[j]
            w[mask] = total
        INF = float('inf')
        dp = [[[INF]*tot for _ in range(m+2)] for __ in range(n+2)]
        dp[sx][sy][0] = 0
        q = deque([(sx, sy, 0)])
        max_profit = -INF
        dx = [-1, 1, 0, 0]
        dy = [0, 0, -1, 1]
        while q:
            x, y, mask = q.popleft()
            if x == sx and y == sy:
                current_profit = w[mask] - dp[x][y][mask]
                max_profit = max(max_profit, current_profit)
            for i in range(4):
                tx, ty = x + dx[i], y + dy[i]
                if tx < 1 or tx > n or ty < 1 or ty > m:
                    continue
                cell = grid[tx-1][ty-1]
                if cell not in ('.', 'S'):
                    continue
                new_mask = mask
                for j in range(m_objects):
                    nx, ny = x, y
                    obj_x, obj_y = gx[j], gy[j]
                    if nx == obj_x and ny < obj_y:
                        if tx < obj_x:
                            new_mask ^= (1 << j)
                    elif tx == obj_x and ty < obj_y:
                        if nx < obj_x:
                            new_mask ^= (1 << j)
                if dp[tx][ty][new_mask] > dp[x][y][mask] + 1:
                    dp[tx][ty][new_mask] = dp[x][y][mask] + 1
                    q.append((tx, ty, new_mask))
        return max(max_profit, 0)
