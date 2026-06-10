import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
from random import randint
from random import random




class CicecaveRewardCalculator(BaseRewardCalculator):
    """Cicecave奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        """从模型输出中提取最后一个[answer]标签内的内容。"""
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.IGNORECASE)
        if not matches:
            return None
        last_answer = matches[-1].strip().upper()
        return last_answer if last_answer in ['YES', 'NO'] else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        """验证答案是否正确。"""
        # 解析实例参数
        n = identity['n']
        m = identity['m']
        grid = [list(row) for row in identity['grid']]
        start = identity['start']
        end = identity['end']
        sx = start[0] - 1
        sy = start[1] - 1
        ex = end[0] - 1
        ey = end[1] - 1
        
        # 获取正确解
        def get_adjacent(x, y):
            directions = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
            return [(nx, ny) for nx, ny in directions if 0 <= nx < n and 0 <= ny < m]
        
        def dfs(sx, sy, ex, ey, grid):
            visited = [[False]*m for _ in range(n)]
            stack = [(sx, sy)]
            visited[sx][sy] = True
            while stack:
                x, y = stack.pop()
                if x == ex and y == ey:
                    return True
                for nx, ny in get_adjacent(x, y):
                    if not visited[nx][ny] and grid[nx][ny] == '.':
                        visited[nx][ny] = True
                        stack.append((nx, ny))
            return False
        
        # 处理起点和终点相同的情况
        if (sx, sy) == (ex, ey):
            adjacent = get_adjacent(sx, sy)
            if any(grid[x][y] == '.' for x, y in adjacent):
                correct = 'YES'
            else:
                correct = 'NO'
        else:
            original_end = grid[ex][ey]
            is_already_cracked = (original_end == 'X')
            grid[ex][ey] = '.'
            
            if is_already_cracked:
                possible = dfs(sx, sy, ex, ey, grid)
                correct = 'YES' if possible else 'NO'
            else:
                adjacent = get_adjacent(ex, ey)
                possible = False
                for x, y in adjacent:
                    if grid[x][y] == '.':
                        grid[x][y] = 'X'
                        if dfs(sx, sy, ex, ey, grid):
                            possible = True
                            grid[x][y] = '.'
                            break
                        grid[x][y] = '.'
                correct = 'YES' if possible else 'NO'
            grid[ex][ey] = original_end  # 恢复现场
        
        return solution == correct
    
    # 其他额外方法

