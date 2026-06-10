import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CfractaldetectorInstructionGenerator(BaseInstructionGenerator):
    """Cfractaldetector Bootcamp指令生成器"""
    
    def __init__(self, max_steps=4, max_size=64):
        """
        初始化Cfractaldetector指令生成器
        
        Args:
            max_steps: 参数描述
            max_size: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_steps = max_steps
        self.max_size = max_size
    
    def case_generator(self):
        mask = random.randint(0, 15)
        possible_steps = []
        for steps in range(2, self.max_steps + 1):
            size = 2 ** (steps + 1)
            if size <= self.max_size:
                possible_steps.append(steps)
        if not possible_steps:
            steps = 2
        else:
            steps = random.choice(possible_steps)
        grid = self.generate_fractal(mask, steps)
        n = len(grid)
        m = len(grid[0]) if n else 0
        return {
            'n': n,
            'm': m,
            'grid': [''.join(row) for row in grid],
            'mask': mask,
            'steps': steps
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""Analyze the {question_case['n']}x{question_case['m']} grid to find valid fractal patterns:
        
Cfractaldetector Rules:
1. Starts with 2x2 pattern (Step 0)
2. Each step:
   - Divide white areas into 4 quadrants
   - Paint using original pattern (black areas stay solid)
3. Minimum 2 steps required (total size ≥8x8)

Grid:
{question_case['n']} {question_case['m']}
""" + '\n'.join(question_case['grid']) + """

Output the count of valid fractal squares as [answer]N[/answer] where N is the number.""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_fractal(mask, steps):
        size = 2 ** (steps + 1)
        grid = [['.' for _ in range(size)] for _ in range(size)]
        kx = [0, 0, 1, 1]
        ky = [0, 1, 0, 1]

        def fill(x, y, block_size, current_step, is_black):
            if current_step > steps:
                for i in range(x, x + block_size):
                    for j in range(y, y + block_size):
                        grid[i][j] = '*' if is_black else '.'
                return

            new_size = block_size // 2
            for q in range(4):
                dx = kx[q] * new_size
                dy = ky[q] * new_size
                nx = x + dx
                ny = y + dy
                if is_black:
                    fill(nx, ny, new_size, current_step + 1, True)
                else:
                    bit = (mask >> (3 - q)) & 1
                    sub_black = bit == 1
                    fill(nx, ny, new_size, current_step + 1, sub_black)

        fill(0, 0, size, 0, False)
        return grid

    @staticmethod
    def count_valid_fractals(grid):
        n, m = len(grid), len(grid[0]) if grid else 0
        if n < 8 or m < 8:
            return 0

        # 修正二维前缀和计算
        sum_ = [[0]*(m+1) for _ in range(n+1)]
        for i in range(1, n+1):
            for j in range(1, m+1):
                sum_[i][j] = sum_[i-1][j] + sum_[i][j-1] - sum_[i-1][j-1] + (1 if grid[i-1][j-1] == '*' else 0)

        MAX_ST = 10
        K = 16
        # 调整DP数组维度顺序
        dp = [[[[False]*m for _ in range(n)] for __ in range(K)] for ___ in range(MAX_ST)]

        # 初始化st=0的状态
        for i in range(n):
            for j in range(m):
                for mask in range(K):
                    dp[0][mask][i][j] = (grid[i][j] == '.')

        # 动态规划状态转移
        for st in range(1, MAX_ST):
            w = 1 << (st-1)
            if 2*w > min(n, m):
                continue
            for mask in range(K):
                for i in range(n - 2*w +1):
                    for j in range(m - 2*w +1):
                        valid = True
                        for q in range(4):
                            x = i + (q//2)*w
                            y = j + (q%2)*w
                            if (mask >> (3-q)) & 1:  # 检查当前象限是否需要全黑
                                # 计算区域全黑的正确公式
                                a, b = x+1, y+1
                                c, d = x + w, y + w
                                total = sum_[c][d] - sum_[a-1][d] - sum_[c][b-1] + sum_[a-1][b-1]
                                if total != w*w:
                                    valid = False
                                    break
                            else:
                                if x >=n or y >=m or not dp[st-1][mask][x][y]:
                                    valid = False
                                    break
                        dp[st][mask][i][j] = valid

        # 统计有效解
        count = 0
        for st in range(2, MAX_ST):
            w = 1 << st
            if 2*w > min(n, m):
                continue
            for i in range(n - 2*w +1):
                for j in range(m - 2*w +1):
                    for mask in range(K):
                        if dp[st][mask][i][j]:
                            count +=1
        return count
