import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EoracandgameoflifeInstructionGenerator(BaseInstructionGenerator):
    """Eoracandgameoflife Bootcamp指令生成器"""
    
    def __init__(self, n=3, m=3, max_p=1e18):
        """
        初始化Eoracandgameoflife指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            max_p: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
        self.max_p = int(max_p)
    
    def case_generator(self):
        # 生成有效测试用例
        while True:
            grid = [
                ''.join(random.choice('01') for _ in range(self.m))
                for _ in range(self.n)
            ]
            
            # 随机选择查询点
            i = random.randint(1, self.n)
            j = random.randint(1, self.m)
            i_idx, j_idx = i-1, j-1
            
            # 计算传播矩阵
            X = compute_X(grid)
            x_val = X[i_idx][j_idx]
            initial = int(grid[i_idx][j_idx])
            
            # 安全生成p值
            try:
                if x_val == 0:
                    p = random.randint(1, self.max_p)
                else:
                    if x_val > 1 and random.random() < 0.5:
                        p = random.randint(1, x_val-1)
                    else:
                        p = random.randint(x_val, min(x_val + 100, self.max_p))
                
                # 计算预期答案
                if x_val == 0 or p < x_val:
                    expected = initial
                else:
                    expected = (initial + (p - x_val + 1) % 2) % 2
                    
                return {
                    'grid': grid,
                    'i': i,
                    'j': j,
                    'p': p,
                    'expected': expected,
                    'X_matrix': X  # 用于调试
                }
            except ValueError:
                continue  # 重新生成非法参数的情况
    
    @staticmethod
    def prompt_func(case):
        grid = '\n'.join(case['grid'])
        return (
            "Orac's Game of Life Challenge\n"
            f"Grid Size: {len(case['grid'])}x{len(case['grid'][0])}\n"
            f"Initial Configuration:\n{grid}\n\n"
            f"Question: What is the color (0/1) of cell ({case['i']}, {case['j']}) "
            f"after {case['p']} iterations?\n\n"
            "Rules:\n"
            "1. Cells flip color if adjacent to same-colored cell\n"
            "2. Changes propagate wave-like through the grid\n"
            "3. Answer format: [answer]N[/answer] where N is 0 or 1\n"
            "Example: [answer]1[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

