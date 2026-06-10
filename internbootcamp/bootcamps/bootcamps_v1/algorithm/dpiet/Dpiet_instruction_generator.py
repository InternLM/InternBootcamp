import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque

# === 源文件中的其他类 ===

class DpietSimulator:
    DIRS = [{'x':0,'y':-1}, {'x':1,'y':0}, {'x':0,'y':1}, {'x':-1,'y':0}]  # 上下左右
    
    def __init__(self, m, n, pixels):
        self.m = m
        self.n = n
        self.pixels = pixels
        self.cols = len(pixels[0])
        self.bp = {'x':0, 'y':0}
        self.dp = 1  # 初始方向：右
        self.cp = 0  # 初始选择器：左
    
    def simulate(self):
        history = []
        colors = []
        
        for _ in range(self.n):
            # 循环检测
            state = (self.bp['x'], self.bp['y'], self.dp, self.cp)
            if state in history:
                idx = history.index(state)
                cycle = colors[idx:]
                return cycle[(self.n - idx) % len(cycle)]
            history.append(state)
            
            # 步骤1：移动到DP方向边缘
            self.move_to_edge(self.dp)
            # 步骤2：移动到CP方向边缘
            self.move_to_edge(self.cp)
            
            # 步骤3：尝试移动
            next_x = self.bp['x'] + self.DIRS[self.dp]['x']
            next_y = self.bp['y'] + self.DIRS[self.dp]['y']
            
            if self.is_out_of_bounds(next_x, next_y) or self.pixels[next_y][next_x] == '0':
                # 处理方向调整
                if self.cp == (self.dp - 1) % 4:
                    self.cp = (self.cp + 2) % 4
                else:
                    self.dp = (self.dp + 1) % 4
                    self.cp = (self.dp - 1) % 4
            else:
                self.bp = {'x': next_x, 'y': next_y}
            
            colors.append(self.pixels[self.bp['y']][self.bp['x']])
        
        return colors[-1]

    def move_to_edge(self, direction):
        current_color = self.pixels[self.bp['y']][self.bp['x']]
        while True:
            next_x = self.bp['x'] + self.DIRS[direction]['x']
            next_y = self.bp['y'] + self.DIRS[direction]['y']
            if self.is_out_of_bounds(next_x, next_y):
                break
            if self.pixels[next_y][next_x] != current_color:
                break
            self.bp = {'x': next_x, 'y': next_y}
    
    def is_out_of_bounds(self, x, y):
        return not (0 <= x < self.cols and 0 <= y < self.m)


class DpietInstructionGenerator(BaseInstructionGenerator):
    """Dpiet Bootcamp指令生成器"""
    
    def __init__(self, max_rows=5, max_cols=5, max_steps=1_000_000):
        """
        初始化Dpiet指令生成器
        
        Args:
            max_rows: 参数描述
            max_cols: 参数描述
            max_steps: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_rows = max_rows
        self.max_cols = max_cols
        self.max_steps = max_steps
    
    def case_generator(self):
        while True:
            try:
                m = random.randint(1, self.max_rows)
                cols = random.randint(1, self.max_cols)
                pixels = self._generate_valid_piet_grid(m, cols)
                n = random.randint(1, self.max_steps)
                expected = self._simulate_piet(m, n, pixels)
                return {
                    'm': m,
                    'n': n,
                    'pixels': pixels,
                    'expected': str(expected)
                }
            except Exception as e:
                continue
    
    @staticmethod
    def prompt_func(question_case):
        grid = '\n'.join(question_case['pixels'])
        return f"""Solve this Dpiet programming puzzle. After exactly {question_case['n']} steps, what is the current color block?

Rules:
- Program is a {question_case['m']}x{len(question_case['pixels'][0])} grid (0=black)
- Blocks are rectangular non-black regions
- IP starts at top-left block, DP=right, CP=left
- Each step:
  1. Move to DP edge within current block
  2. Move to CP edge within current block 
  3. Attempt DP move:
     - Success: Enter new block
     - Failure: 
       If CP was left → switch to right
       If CP was right → rotate DP 90° clockwise and reset CP to left

Input:
{question_case['m']} {question_case['n']}
{grid}

Output your answer between [answer] and [/answer], e.g. [answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_piet_grid(self, m, cols):
        grid = [['0']*cols for _ in range(m)]
        colors = deque(random.sample('123456789', k=9))
        visited = [[False]*cols for _ in range(m)]

        # 生成初始块（包含(0,0)）
        color = colors.popleft()
        max_h = min(random.randint(1, m), m)
        max_w = min(random.randint(1, cols), cols)
        for i in range(max_h):
            for j in range(max_w):
                grid[i][j] = color
                visited[i][j] = True

        # 生成后续色块
        while colors:
            candidates = []
            for i in range(m):
                for j in range(cols):
                    if not visited[i][j]:
                        if (i == 0 or visited[i-1][j]) and (j == 0 or visited[i][j-1]):
                            max_h_block = 1
                            while i+max_h_block < m and not visited[i+max_h_block][j]:
                                max_h_block += 1
                            max_w_block = 1
                            while j+max_w_block < cols and not visited[i][j+max_w_block]:
                                max_w_block += 1
                            if max_h_block >=1 and max_w_block >=1:
                                candidates.append((i,j,max_h_block,max_w_block))

            if not candidates:
                break

            i,j,h_max,w_max = random.choice(candidates)
            color = colors.popleft()
            h = random.randint(1, h_max)
            w = random.randint(1, w_max)

            for di in range(h):
                for dj in range(w):
                    if i+di < m and j+dj < cols:
                        grid[i+di][j+dj] = color
                        visited[i+di][j+dj] = True

        return [''.join(row) for row in grid]

    @staticmethod
    def _simulate_piet(m, n, pixels):
        simulator = DpietSimulator(m, n, pixels)
        return simulator.simulate()
