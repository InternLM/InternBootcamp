import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque

# === 源文件中的全局函数 ===

def get_adj(x, y, n_rows, m_cols):
    return [(nx, ny) for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)] 
            if 0<=(nx:=x+dx)<m_cols and 0<=(ny:=y+dy)<n_rows]

def solve_maze(n, m, original_grid):
    grid = [row.copy() for row in original_grid]
    good = set()
    bad = []
    
    # 收集所有好人坏人位置
    for y in range(n):
        for x in range(m):
            if grid[y][x] == 'G':
                good.add((y,x))
            elif grid[y][x] == 'B':
                bad.append((y,x))
    
    # 处理坏人周围的墙
    valid = True
    for y, x in bad:
        # 检查坏人是否离出口太近（曼哈顿距离）
        if (n-1 - y) + (m-1 - x) <= 1:
            valid = False
        
        # 将坏人周围的空地变为墙
        for ax, ay in get_adj(x, y, n, m):
            if grid[ay][ax] == '.':
                grid[ay][ax] = '#'
        
        if not valid: break
    
    # 提前终止条件
    if not valid:
        return "Yes" if len(good) == 0 else "No"
    
    # 出口被墙阻挡的情况
    if grid[n-1][m-1] == '#':
        return "Yes" if len(good) == 0 else "No"
    
    # BFS检查可达性
    marked = [[False]*m for _ in range(n)]
    queue = deque([(n-1, m-1)])
    marked[n-1][m-1] = True
    valid = True
    
    while queue:
        y, x = queue.popleft()
        
        # 遇到坏人直接失败
        if grid[y][x] == 'B':
            valid = False
            break
        
        # 处理相邻单元格
        for ax, ay in get_adj(x, y, n, m):
            if not marked[ay][ax] and grid[ay][ax] != '#':
                marked[ay][ax] = True
                queue.append((ay, ax))
                if (ay, ax) in good:
                    good.remove((ay, ax))
    
    return "Yes" if valid and not good else "No"


class DsolvethemazeInstructionGenerator(BaseInstructionGenerator):
    """Dsolvethemaze Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=50, min_m=1, max_m=50):
        """
        初始化Dsolvethemaze指令生成器
        
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
        grid = []
        for y in range(n):
            row = []
            for x in range(m):
                # 确保出口单元格（n-1,m-1）初始为空
                if y == n-1 and x == m-1:
                    row.append('.')
                else:
                    row.append(random.choice(['.', '#', 'G', 'B']))
            grid.append(row)
        return {'n':n, 'm':m, 'grid':grid}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid_str = '\n'.join(''.join(row) for row in question_case['grid'])
        return f"""Given a {question_case['n']}x{question_case['m']} maze grid where:
- '.' = empty cell
- '#' = wall
- 'G' = good person
- 'B' = bad person

Exit is at bottom-right cell ({question_case['n']}, {question_case['m']}). Can we block cells (turn '.' to '#') such that:
1. All G can reach exit
2. All B cannot reach exit

Maze layout:
{grid_str}

Answer with [answer]Yes[/answer] or [answer]No[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

