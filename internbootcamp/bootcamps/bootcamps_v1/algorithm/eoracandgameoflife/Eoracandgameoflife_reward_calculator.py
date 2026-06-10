import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import heapq
import random
import re

# === 源文件中的全局函数 ===

def compute_X(grid):
    n = len(grid)
    m = len(grid[0]) if n else 0
    A = [[int(c) for c in row] for row in grid]
    X = [[0]*m for _ in range(n)]
    heap = []
    
    # 定义四个方向
    directions = [(-1,0), (1,0), (0,-1), (0,1)]
    
    # 初始化传播队列
    for i in range(n):
        for j in range(m):
            has_same = False
            current = A[i][j]
            # 检查相邻单元格
            for dx, dy in directions:
                ni, nj = i+dx, j+dy
                if 0 <= ni < n and 0 <= nj < m and A[ni][nj] == current:
                    has_same = True
                    break
            if has_same:
                X[i][j] = 1
                heapq.heappush(heap, (1, i, j))
    
    # BFS传播更新
    while heap:
        step, i, j = heapq.heappop(heap)
        for dx, dy in directions:
            ni, nj = i + dx, j + dy
            if 0 <= ni < n and 0 <= nj < m and X[ni][nj] == 0:
                X[ni][nj] = step + 1
                heapq.heappush(heap, (step+1, ni, nj))
    return X


class EoracandgameoflifeRewardCalculator(BaseRewardCalculator):
    """Eoracandgameoflife奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 严格匹配最后一个答案标签
        matches = re.findall(r'\[answer\s*\]\s*(\d)\s*\[/answer\s*\]', output, re.IGNORECASE)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        try:
            return solution == str(case['expected'])
        except:
            return False
    
    # 其他额外方法

