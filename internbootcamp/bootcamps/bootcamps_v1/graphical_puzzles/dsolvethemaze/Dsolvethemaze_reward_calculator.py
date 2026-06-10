import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class DsolvethemazeRewardCalculator(BaseRewardCalculator):
    """Dsolvethemaze奖励计算器"""
    
    @staticmethod 
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](yes|no)\[/answer\]', output, re.I)
        return matches[-1].title() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == solve_maze(identity['n'], identity['m'], identity['grid'])
    
    # 其他额外方法

