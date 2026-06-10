import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import json
import random
import re
import ast
from itertools import combinations




class LightupRewardCalculator(BaseRewardCalculator):
    """Lightup奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 使用非贪婪匹配查找最后一个answer标签
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        
        try:
            # 清理字符串并解析
            last_match = matches[-1].strip().replace(' ', '').replace('\n', '')
            return ast.literal_eval(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        grid = identity['grid']
        rows = identity['rows']
        cols = identity['cols']
        bulbs = solution

        # 验证1: 所有灯泡在白色格子
        for x, y in bulbs:
            if not (0 <= x < rows and 0 <= y < cols):
                return False
            if not grid[x][y].startswith('W'):
                return False

        # 验证2: 数字黑格子条件
        for i in range(rows):
            for j in range(cols):
                cell = grid[i][j]
                if cell.startswith('B') and len(cell) > 1 and cell[1].isdigit():
                    required = int(cell[1])
                    count = 0
                    # 检查四个方向
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        ni, nj = i+dx, j+dy
                        if 0 <= ni < rows and 0 <= nj < cols:
                            if (ni, nj) in bulbs:
                                count += 1
                    if count != required:
                        return False

        # 验证3: 所有白色格子被照亮
        for i in range(rows):
            for j in range(cols):
                if grid[i][j].startswith('W'):
                    illuminated = False
                    for bx, by in bulbs:
                        # 检查行可见
                        if bx == i:
                            min_y = min(by, j)
                            max_y = max(by, j)
                            blocked = False
                            for y in range(min_y+1, max_y):
                                if grid[bx][y].startswith('B'):
                                    blocked = True
                                    break
                            if not blocked:
                                illuminated = True
                                break
                        # 检查列可见
                        if by == j:
                            min_x = min(bx, i)
                            max_x = max(bx, i)
                            blocked = False
                            for x in range(min_x+1, max_x):
                                if grid[x][by].startswith('B'):
                                    blocked = True
                                    break
                            if not blocked:
                                illuminated = True
                                break
                    if not illuminated:
                        return False

        # 验证4: 灯泡之间无冲突
        for (x1, y1), (x2, y2) in combinations(bulbs, 2):
            if x1 == x2:
                min_y = min(y1, y2)
                max_y = max(y1, y2)
                blocked = False
                for y in range(min_y+1, max_y):
                    if grid[x1][y].startswith('B'):
                        blocked = True
                        break
                if not blocked:
                    return False
            elif y1 == y2:
                min_x = min(x1, x2)
                max_x = max(x1, x2)
                blocked = False
                for x in range(min_x+1, max_x):
                    if grid[x][y1].startswith('B'):
                        blocked = True
                        break
                if not blocked:
                    return False

        return True
    
    # 其他额外方法

