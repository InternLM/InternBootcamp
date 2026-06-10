import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque
import re




class CgardenofthesunInstructionGenerator(BaseInstructionGenerator):
    """Cgardenofthesun Bootcamp指令生成器"""
    
    def __init__(self, n_range=(3, 10), m_range=(3, 10)):
        """
        初始化Cgardenofthesun指令生成器
        
        Args:
            n_range: 参数描述
            m_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = n_range
        self.m_range = m_range
    
    def case_generator(self):
        n = random.randint(*self.n_range)
        m = random.randint(*self.m_range)
        
        # 确保至少有一个初始X
        while True:
            solution = self.generate_tree(n, m)
            initial_x = self.create_valid_initial_x(solution)
            if initial_x:
                break
        
        initial_grid = self.create_initial_grid(n, m, initial_x)
        
        return {
            'n': n,
            'm': m,
            'initial_grid': initial_grid,
            'expected_solution': solution
        }
    
    @staticmethod
    def prompt_func(case) -> str:
        grid = '\n'.join(case['initial_grid'])
        return f"""你需要解决一个花园迷宫问题。现有网格如下（X表示空单元格，.表示有向日葵）：
{grid}

要求：
1. 最终所有X必须连通（四方向移动）
2. X之间构成无环树结构
3. 必须保留所有原始X
4. 只能通过添加新的X（移除向日葵）来满足条件

将答案放在[answer]标签内，每行表示网格。示例：
[answer]
XXX
.X.
XXX
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_tree(self, n, m):
        """使用Prim算法生成生成树结构"""
        grid = [[False for _ in range(m)] for _ in range(n)]
        directions = [(-1,0), (0,1), (1,0), (0,-1)]

        # 随机选择起点
        start = (random.randint(0, n-1), random.randint(0, m-1))
        grid[start[0]][start[1]] = True
        frontier = []

        # 初始化边界
        for dx, dy in directions:
            nx, ny = start[0]+dx, start[1]+dy
            if 0 <= nx < n and 0 <= ny < m:
                frontier.append((nx, ny))

        while frontier:
            # 随机选择边界点
            idx = random.randint(0, len(frontier)-1)
            x, y = frontier.pop(idx)

            # 寻找相邻的已选节点
            neighbors = []
            for dx, dy in directions:
                nx, ny = x+dx, y+dy
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny]:
                    neighbors.append((nx, ny))

            if neighbors:
                # 随机选择一个邻居连接
                parent = random.choice(neighbors)
                grid[x][y] = True

                # 添加新边界
                for dx, dy in directions:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < n and 0 <= ny < m and not grid[nx][ny]:
                        if (nx, ny) not in frontier:
                            frontier.append((nx, ny))

        return grid

    def create_valid_initial_x(self, solution):
        """生成满足条件的初始X集合"""
        n, m = len(solution), len(solution[0])
        candidates = [(i,j) for i in range(n) for j in range(m) if solution[i][j]]
        initial = set()
        banned = set()

        # 随机打乱候选顺序
        random.shuffle(candidates)

        for x, y in candidates:
            # 检查8邻域是否冲突
            conflict = False
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if (x+dx, y+dy) in initial:
                        conflict = True
                        break
                if conflict:
                    break
            if not conflict:
                initial.add((x, y))
                # 将周围8格标记为禁止区
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        banned.add((x+dx, y+dy))

        return initial

    def create_initial_grid(self, n, m, initial_x):
        grid = [['.' for _ in range(m)] for _ in range(n)]
        for x, y in initial_x:
            grid[x][y] = 'X'
        return [''.join(row) for row in grid]
