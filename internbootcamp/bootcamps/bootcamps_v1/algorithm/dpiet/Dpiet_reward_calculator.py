import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class DpietRewardCalculator(BaseRewardCalculator):
    """Dpiet奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1] if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['expected']
    
    # 其他额外方法

