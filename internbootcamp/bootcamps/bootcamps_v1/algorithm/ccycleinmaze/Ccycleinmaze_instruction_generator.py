import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import deque
import random
import re




class CcycleinmazeInstructionGenerator(BaseInstructionGenerator):
    """Ccycleinmaze Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ccycleinmaze指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params.copy()
        # 调整默认参数确保迷宫可解性
        self.params.setdefault('max_n', 5)
        self.params.setdefault('max_m', 5)
        self.params.setdefault('min_k', 2)
        self.params.setdefault('max_k', 20)
        self.params.setdefault('obstacle_prob', 0.3)
        # 确保生成的k是偶数概率更高
        self.params.setdefault('even_k_prob', 0.8)
    
    def case_generator(self):
        # 参数设定优化
        max_n = self.params['max_n']
        max_m = self.params['max_m']
        min_k = self.params['min_k']
        max_k = self.params['max_k']
        obstacle_prob = self.params['obstacle_prob']
        even_k_prob = self.params['even_k_prob']
        
        # 生成k值，控制偶数概率
        if random.random() < even_k_prob:
            k = 2 * random.randint(min_k//2, (max_k+1)//2)
            if k == 0:  # 确保最小k为2
                k = 2
        else:
            k = random.randint(min_k, max_k)
        
        # 生成初始位置和迷宫
        while True:
            n = random.randint(1, max_n)
            m = random.randint(1, max_m)
            x, y = random.randint(0, n-1), random.randint(0, m-1)
            
            # 生成迷宫时确保至少一个可移动方向
            grid = []
            valid_directions = 0
            for i in range(n):
                row = []
                for j in range(m):
                    if i == x and j == y:
                        row.append('X')
                    else:
                        if (abs(i-x) + abs(j-y)) == 1:  # 邻接位置减少障碍概率
                            prob = obstacle_prob / 2
                        else:
                            prob = obstacle_prob
                        cell = '*' if random.random() < prob else '.'
                        row.append(cell)
                        # 统计初始可移动方向
                        if cell == '.' and (abs(i-x) + abs(j-y)) == 1:
                            valid_directions += 1
                grid.append(''.join(row))
            
            # 如果初始位置完全被阻塞且k>0，重新生成
            if valid_directions == 0 and k > 0:
                continue
            else:
                break
        
        # 生成正确答案
        correct_answer = self._generate_solution(n, m, k, grid)
        return {
            'n': n,
            'm': m,
            'k': k,
            'grid': grid,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        grid = "\n".join(question_case['grid'])
        return f"""You control a robot in a {question_case['n']}x{question_case['m']} maze. The robot starts at 'X' and must return after exactly {question_case['k']} moves. Find the lexicographically smallest path using moves D (down), L (left), R (right), U (up). 

Maze Layout:
{grid}

Rules:
1. Moves are ordered by lex priority: D < L < R < U
2. Each move must be to an empty cell (.) or back to start
3. Path length must be exactly {question_case['k']}
4. If impossible, respond with IMPOSSIBLE

Format your answer between [answer] and [/answer]. Example: [answer]DLRU[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_solution(n, m, k, grid):
        """ 使用BFS生成正确答案 """
        if k % 2 != 0:
            return "IMPOSSIBLE"

        # 查找起始点
        start_x, start_y = -1, -1
        for i in range(n):
            for j in range(m):
                if grid[i][j] == 'X':
                    start_x, start_y = i, j
                    break
            if start_x != -1:
                break

        dx = [1, 0, 0, -1]  # D, L, R, U
        dy = [0, -1, 1, 0]
        dirs = ['D', 'L', 'R', 'U']
        size = n * m
        dist = [float('inf')] * size
        q = deque([(start_x, start_y, 0)])
        dist[start_x * m + start_y] = 0

        # BFS计算最短路径
        while q:
            x, y, d = q.popleft()
            for i in range(4):
                nx, ny = x + dx[i], y + dy[i]
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] != '*':
                    pos = nx * m + ny
                    if dist[pos] > d + 1:
                        dist[pos] = d + 1
                        q.append((nx, ny, d + 1))

        path = []
        x, y = start_x, start_y
        for step in range(k):
            found = False
            for i in range(4):  # 按字典序选择方向
                nx = x + dx[i]
                ny = y + dy[i]
                if 0 <= nx < n and 0 <= ny < m and grid[nx][ny] != '*':
                    pos = nx * m + ny
                    remaining = k - step - 1
                    if dist[pos] <= remaining:
                        path.append(dirs[i])
                        x, y = nx, ny
                        found = True
                        break
            if not found:
                return "IMPOSSIBLE"

        # 最终必须回到起点
        return ''.join(path) if (x, y) == (start_x, start_y) else "IMPOSSIBLE"
