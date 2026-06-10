import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
from collections import deque




class HeyawakeInstructionGenerator(BaseInstructionGenerator):
    """Heyawake Bootcamp指令生成器"""
    
    def __init__(self, rows=3, cols=3):
        """
        初始化Heyawake指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        # 生成一个简单的谜题实例，房间0的number为0，确保有解
        rows = self.rows
        cols = self.cols
        rooms = [
            {
                'cells': [(0, 0)],
                'number': 0
            },
            {
                'cells': [(i, j) for i in range(rows) for j in range(cols) if (i, j) != (0, 0)]
                # 无number
            }
        ]
        return {
            'rows': rows,
            'cols': cols,
            'rooms': rooms
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        rows = question_case['rows']
        cols = question_case['cols']
        rooms = question_case['rooms']
        problem_desc = "请解决以下Heyawake谜题：\n\n"
        problem_desc += "谜题规则：\n"
        problem_desc += "1. 黑格不能水平或垂直相邻。\n"
        problem_desc += "2. 每个带有数字的房间必须包含恰好该数字的黑格。未带数字的房间可以有任何数量的黑格。\n"
        problem_desc += "3. 所有白格必须形成一个连通的区域。\n"
        problem_desc += "4. 同一行或列中的连续白格不能跨越三个或更多不同的房间。\n\n"
        problem_desc += f"网格尺寸：{rows}行×{cols}列。\n"
        problem_desc += "房间划分及其数字说明：\n"
        for idx, room in enumerate(rooms):
            cells = room['cells']
            number = room.get('number', None)
            cells_str = ', '.join(f'({r},{c})' for r, c in cells)
            problem_desc += f"- 房间{idx+1}包含单元格 {cells_str}"
            if number is not None:
                problem_desc += f"，必须恰好有 {number} 个黑格"
            problem_desc += "。\n"
        problem_desc += "\n将答案以二维数组（0为白格，1为黑格）放在[answer]标签内，例如：\n[answer]\n[[0, 0, 0],\n[0, 1, 0],\n[0, 0, 0]]\n[/answer]"
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

