import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from ast import literal_eval




class KakuroInstructionGenerator(BaseInstructionGenerator):
    """Kakuro Bootcamp指令生成器"""
    
    def __init__(self, rows=3, cols=3):
        """
        初始化Kakuro指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        # 生成横向序列的数对
        a, b = self._generate_unique_pair()
        sum_r = a + b
        
        # 生成纵向序列的数对
        c, d = self._generate_unique_pair()
        sum_d = c + d
        
        # 构建网格结构
        grid = [[{'type': 'black', 'right': (sum_r, 2), 'down': (sum_d, 2)} if (row == 0 and col == 0) else
                {'type': 'white'} if ((row == 0 and col in (1, 2)) or (col == 0 and row in (1, 2))) else
                {'type': 'black'} for col in range(self.cols)] for row in range(self.rows)]
        
        solution = {
            "(0, 1)": a,
            "(0, 2)": b,
            "(1, 0)": c,
            "(2, 0)": d
        }
        
        return {
            'grid': grid,
            'solution': solution
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        clues = []
        grid = question_case['grid']
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                if cell['type'] == 'black':
                    parts = []
                    if 'right' in cell:
                        sum_r, len_r = cell['right']
                        parts.append(f"右侧的 {len_r} 个白色格子之和为 {sum_r}")
                    if 'down' in cell:
                        sum_d, len_d = cell['down']
                        parts.append(f"下方的 {len_d} 个白色格子之和为 {sum_d}")
                    if parts:
                        clues.append(f"位于 ({row_idx}, {col_idx}) 的黑色格子：" + "，".join(parts))
        clues_text = "\n".join(clues)
        
        white_coords = []
        for row_idx, row in enumerate(grid):
            for col_idx, cell in enumerate(row):
                if cell['type'] == 'white':
                    white_coords.append(f"({row_idx}, {col_idx})")
        white_coords_text = ", ".join(white_coords)
        
        prompt = f"""你是Kakuro谜题解答者，请根据以下线索填充所有白色格子，确保每个横向或纵向的序列满足和的条件，且同一序列中的数字不重复。每个格子只能填1-9的整数。

谜题线索：
{clues_text}

需要填充的白色格子位于以下坐标：{white_coords_text}。

请将你的答案以字典形式放在[answer]和[/answer]之间，键为坐标字符串，如"(行,列)"，值为对应的整数。例如：
[answer]
{{"(0,1)": 3, "(0,2)": 4, "(1,0)":5, "(2,0)":2}}
[/answer]
请确保所有白色格子都被正确填写，且没有多余或缺少的项。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_unique_pair(self):
        while True:
            a = random.randint(1, 9)
            b = random.randint(1, 9)
            if a != b:
                return a, b
