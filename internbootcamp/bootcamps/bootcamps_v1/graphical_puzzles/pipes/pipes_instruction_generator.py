import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import re
from typing import Dict
from typing import List
from typing import Tuple




class PipesInstructionGenerator(BaseInstructionGenerator):
    """Pipes Bootcamp指令生成器"""
    
    def __init__(self, rows=5, cols=5, num_colors=2):
        """
        初始化Pipes指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
            num_colors: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = rows
        self.cols = cols
        self.num_colors = num_colors
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange'][:num_colors]
    
    def case_generator(self) -> dict:
        col_split = []
        base_cols = self.cols // self.num_colors
        remainder = self.cols % self.num_colors
        current = 0
        for i in range(self.num_colors):
            add = 1 if i < remainder else 0
            col_width = base_cols + add
            col_split.append((current, current + col_width))
            current += col_width

        endpoints = {}
        solution_paths = {}
        for i in range(self.num_colors):
            color = self.colors[i]
            start_col, end_col = col_split[i]
            path = []
            for row in range(self.rows):
                if row % 2 == 0:
                    cols_in_row = range(start_col, end_col)
                else:
                    cols_in_row = range(end_col-1, start_col-1, -1)
                for col in cols_in_row:
                    path.append((row, col))
            start = path[0]
            end = path[-1]
            endpoints[color] = [list(start), list(end)]
            solution_paths[color] = [list(coord) for coord in path]

        return {
            'grid_size': [self.rows, self.cols],
            'endpoints': endpoints,
            'solution_paths': solution_paths
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid_size = question_case['grid_size']
        endpoints = question_case['endpoints']
        prompt = (
            f"You are playing a 'Pipes' puzzle on a {grid_size[0]}x{grid_size[1]} grid. Connect each pair of colored endpoints "
            "with continuous, non-overlapping paths that fill all cells. Follow these rules:\n"
            "1. Paths must be straight lines (horizontal/vertical)\n"
            "2. All cells must be filled\n"
            "3. Paths cannot cross or overlap\n\n"
            "Endpoints positions:\n"
        )
        for color, points in endpoints.items():
            prompt += f"- {color}: Start at {points[0]}, End at {points[1]}\n"
        prompt += (
            "\nFormat your answer as a JSON dictionary where keys are colors and values are coordinate lists "
            "from start to end. Enclose your answer within [answer] and [/answer] tags.\n"
            "Example:\n[answer]\n{\n  \"red\": [[0,0], [0,1], [1,1]],\n  \"blue\": [[2,2], [2,3]]\n}\n[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

