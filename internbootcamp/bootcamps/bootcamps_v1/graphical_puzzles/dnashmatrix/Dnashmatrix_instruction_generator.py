import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class DnashmatrixInstructionGenerator(BaseInstructionGenerator):
    """Dnashmatrix Bootcamp指令生成器"""
    
    def __init__(self, n=3, x_prob=0.2, invalid_prob=0.3):
        """
        初始化Dnashmatrix指令生成器
        
        Args:
            n: 参数描述
            x_prob: 参数描述
            invalid_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.x_prob = x_prob
        self.invalid_prob = invalid_prob  # 生成无效案例的概率
    
    def case_generator(self):
        if random.random() < self.invalid_prob:
            return self.generate_invalid_case()
        else:
            return self.generate_valid_case()
    
    @staticmethod
    def prompt_func(question_case):
        """构造完整的谜题描述"""
        n = question_case['n']
        cells = question_case['cells']
        input_lines = [str(n)]
        for row in cells:
            parts = []
            for cell in row:
                if cell == (-1, -1):
                    parts.extend([-1, -1])
                else:
                    x, y = cell
                    parts.extend([x, y])
            input_lines.append(' '.join(map(str, parts)))
        problem = f"""Alice设计了一个棋盘游戏，其中每个单元格包含一个指令（U、D、L、R或X）。玩家根据指令移动，直到进入X（阻塞区）或无限循环。给定每个单元格的终止点或标记为无限循环的信息，请判断是否存在有效的棋盘。如果存在，输出VALID并给出一个可能的解；否则，输出INVALID。

输入数据：
第一行是一个整数n，表示棋盘的大小。
接下来n行，每行包含2n个整数，按顺序表示每个单元格的终止点坐标或(-1,-1)。

输入示例：
{chr(10).join(input_lines)}

将答案放置在[answer]标签内。例如：
[answer]
VALID
XL
RX
[/answer]
或：
[answer]
INVALID
[/answer]"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_case(self):
        """生成有效案例并标记is_valid=True"""
        grid = self.generate_valid_grid()
        valid_cells = self.simulate_grid(grid)
        return {
            "n": self.n,
            "cells": valid_cells,
            "is_valid": True
        }

    def generate_invalid_case(self):
        """生成无效案例并标记is_valid=False"""
        n = self.n
        # 创建一个必定矛盾的案例：所有单元格要求最终到达同一个X但路径冲突
        valid_grid = self.generate_valid_grid()
        cells = self.simulate_grid(valid_grid)
        # 随机选择一个单元格，强制其终止点为另一个单元格，但该单元格并非X且路径无法到达
        i, j = random.randint(0, n-1), random.randint(0, n-1)
        target = (random.randint(1, n), random.randint(1, n))
        while target == (i+1, j+1) or valid_grid[i][j] == 'X':
            i, j = random.randint(0, n-1), random.randint(0, n-1)
            target = (random.randint(1, n), random.randint(1, n))
        cells[i][j] = target
        return {
            "n": n,
            "cells": cells,
            "is_valid": False  # 强制标记为无效
        }

    def generate_valid_grid(self):
        """生成合法网格，确保指令不会导致越界"""
        grid = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                possible = []
                if i > 0:
                    possible.append('U')
                if i < self.n - 1:
                    possible.append('D')
                if j > 0:
                    possible.append('L')
                if j < self.n - 1:
                    possible.append('R')
                possible.append('X')
                # 优先设置X的概率
                if random.random() < self.x_prob:
                    char = 'X'
                else:
                    char = random.choice(possible)
                row.append(char)
            grid.append(row)
        return grid

    def simulate_grid(self, grid):
        """计算每个单元格的终止点"""
        cells = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                termination = self.simulate_cell(i, j, grid)
                row.append(termination)
            cells.append(row)
        return cells

    def simulate_cell(self, r, c, grid):
        """模拟玩家移动，返回终止点或(-1,-1)"""
        visited = set()
        current_r, current_c = r, c
        while True:
            if (current_r, current_c) in visited:
                return (-1, -1)
            visited.add((current_r, current_c))
            char = grid[current_r][current_c]
            if char == 'X':
                return (current_r + 1, current_c + 1)
            elif char == 'U':
                current_r -= 1
            elif char == 'D':
                current_r += 1
            elif char == 'L':
                current_c -= 1
            elif char == 'R':
                current_c += 1

    @classmethod
    def check_valid_solution(cls, solution_lines, identity):
        """验证有效案例的网格正确性"""
        n = identity["n"]
        if len(solution_lines) != n + 1:
            return False
        grid = solution_lines[1:]
        # 格式检查
        for row in grid:
            if len(row) != n or any(c not in "UDLRX" for c in row):
                return False
        # 指令合法性检查
        for i in range(n):
            for j in range(n):
                c = grid[i][j]
                if (c == 'U' and i == 0) or (c == 'D' and i == n-1) or \
                   (c == 'L' and j == 0) or (c == 'R' and j == n-1):
                    return False
        # 终止点一致性检查
        for i in range(n):
            for j in range(n):
                simulated = cls.static_simulate_cell(i, j, grid)
                expected = identity["cells"][i][j]
                if simulated != expected:
                    return False
        return True

    @staticmethod
    def static_simulate_cell(r, c, grid):
        """静态方法：模拟单元格移动"""
        n = len(grid)
        visited = set()
        current_r, current_c = r, c
        while True:
            if (current_r, current_c) in visited:
                return (-1, -1)
            visited.add((current_r, current_c))
            char = grid[current_r][current_c]
            if char == 'X':
                return (current_r + 1, current_c + 1)
            elif char == 'U':
                current_r -= 1
            elif char == 'D':
                current_r += 1
            elif char == 'L':
                current_c -= 1
            elif char == 'R':
                current_c += 1
