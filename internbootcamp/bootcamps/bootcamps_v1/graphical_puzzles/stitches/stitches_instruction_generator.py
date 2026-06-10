import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict




class StitchesInstructionGenerator(BaseInstructionGenerator):
    """Stitches Bootcamp指令生成器"""
    
    def __init__(self, rows=5, cols=5):
        """
        初始化Stitches指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        numbered_cells = []
        # Generate outer perimeter as solution
        perimeter_points = self._get_perimeter_points()
        # Add numbered cells: select some perimeter points as 2, some inner points as 0
        for x in range(self.rows):
            for y in range(self.cols):
                if (x, y) in perimeter_points:
                    if random.random() < 0.3:  # 30% chance to mark as 2
                        numbered_cells.append({'x': x, 'y': y, 'num': 2})
                else:
                    if random.random() < 0.1:  # 10% chance to mark inner as 0
                        numbered_cells.append({'x': x, 'y': y, 'num': 0})
        return {
            'rows': self.rows,
            'cols': self.cols,
            'numbered_cells': numbered_cells
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        rows = question_case['rows']
        cols = question_case['cols']
        cells = question_case['numbered_cells']
        cells_desc = '\n'.join([f"- 坐标 ({c['x']}, {c['y']}) 的数值为 {c['num']}" for c in cells])
        return f"""你是一个Stitches Puzzle解题专家，请根据以下规则解决谜题：

**规则说明**
1. 目标：在{rows}x{cols}的点阵中绘制水平/垂直缝线，形成**唯一闭合环**（无交叉、无分支）。
2. 数字规则：
   - 数字N表示该点必须连接N条缝线
   - 数值0必须无连接，数值2必须连接两条
3. 未标数字的点属于环时必须有2条缝线
4. 缝线必须形成连续闭合环，所有点至多属于一个环

**当前谜题**
数字点列表（坐标从0开始）：
{cells_desc if cells else "无数字点"}

**答案格式**
请将答案包含在[answer]和[/answer]之间，格式为：
[[(x1,y1),(x2,y2)], [(x3,y3),(x4,y4)], ...]
确保每个缝线为相邻点坐标，如示例所示。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _get_perimeter_points(self):
        points = set()
        for x in [0, self.rows-1]:
            for y in range(self.cols):
                points.add((x, y))
        for y in [0, self.cols-1]:
            for x in range(1, self.rows-1):
                points.add((x, y))
        return points
