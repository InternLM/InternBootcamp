import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random
import re
import ast
from itertools import combinations




class LightupInstructionGenerator(BaseInstructionGenerator):
    """Lightup Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Lightup指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = params.get('rows', 5)
        self.cols = params.get('cols', 5)
        self.max_attempts = params.get('max_attempts', 100)
        self.min_black_cells = params.get('min_black_cells', 3)
        self.max_black_cells = params.get('max_black_cells', 8)
    
    def case_generator(self):
        # 生成有效谜题的简单实现（示例性质，实际需要更健壮的实现）
        # 这里采用一个简化方法：生成一个包含中心灯泡和必要黑色格子的网格
        grid = [['W' for _ in range(self.cols)] for _ in range(self.rows)]
        bulbs = []

        # 随机生成一些黑格子
        black_cells = random.randint(self.min_black_cells, self.max_black_cells)
        for _ in range(black_cells):
            x = random.randint(0, self.rows-1)
            y = random.randint(0, self.cols-1)
            grid[x][y] = 'B'

        # 尝试放置灯泡（示例位置）
        # 注意：这是简化实现，实际需要确保符合所有规则
        if self.rows >= 3 and self.cols >= 3:
            x, y = self.rows//2, self.cols//2
            if grid[x][y] == 'W':
                bulbs.append((x, y))
                grid[x][y] = 'B'  # 转换为黑格子来防止互相照射（示例逻辑）

        # 设置黑格子数字（示例逻辑）
        for i in range(self.rows):
            for j in range(self.cols):
                if grid[i][j] == 'B':
                    count = 0
                    # 检查四个方向
                    dirs = [(-1,0), (1,0), (0,-1), (0,1)]
                    for dx, dy in dirs:
                        ni, nj = i+dx, j+dy
                        if 0 <= ni < self.rows and 0 <= nj < self.cols:
                            if (ni, nj) in bulbs:
                                count += 1
                    if count > 0:
                        grid[i][j] = f'B{count}'

        # 转换为可JSON序列化的格式
        return {
            'grid': grid,
            'rows': self.rows,
            'cols': self.cols
        }
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case['grid']
        rows = question_case['rows']
        cols = question_case['cols']
        
        prompt = """你是一个专业灯谜解题者，请根据以下规则在网格中放置灯泡：

规则：
1. 灯泡只能放在白色格子（□）中，放置后可以照亮整行和整列直到被黑色格子阻挡
2. 任何两个灯泡不能互相照射（同一行/列直接可见）
3. 数字黑色格子（如■3）表示相邻（上下左右）的白色格子中必须放置正好对应数量的灯泡
4. 所有白色格子必须被至少一个灯泡照亮

网格布局（行号0-{}，列号0-{}）：
""".format(rows-1, cols-1)

        # 构建网格可视化
        for i in range(rows):
            line = []
            for j in range(cols):
                cell = grid[i][j]
                if cell == 'W':
                    line.append('□')
                elif cell.startswith('B'):
                    if len(cell) > 1 and cell[1].isdigit():
                        line.append(f'■{cell[1]}')
                    else:
                        line.append('■')
                else:
                    line.append('?')
            prompt += f"行{i}：" + " ".join(line) + "\n"

        prompt += "\n请将答案的灯泡坐标列表放在[answer]标签内，例如：[answer][(1,2), (3,4)][/answer]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

