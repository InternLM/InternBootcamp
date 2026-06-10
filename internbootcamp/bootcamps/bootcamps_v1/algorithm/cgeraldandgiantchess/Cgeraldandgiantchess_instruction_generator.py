import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class CgeraldandgiantchessInstructionGenerator(BaseInstructionGenerator):
    """Cgeraldandgiantchess Bootcamp指令生成器"""
    
    def __init__(self, h_min=1, h_max=20, w_min=1, w_max=20, max_black=10):
        """
        初始化Cgeraldandgiantchess指令生成器
        
        Args:
            h_min: 参数描述
            h_max: 参数描述
            w_min: 参数描述
            w_max: 参数描述
            max_black: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.h_min = h_min
        self.h_max = h_max
        self.w_min = w_min
        self.w_max = w_max
        self.max_black = max_black
    
    def case_generator(self):
        # 生成合法棋盘尺寸
        h = random.randint(self.h_min, self.h_max)
        w = random.randint(self.w_min, self.w_max)
        
        # 生成所有可能黑格（排除起点和终点）
        forbidden = {(1, 1), (h, w)}
        all_cells = [
            (r, c)
            for r in range(1, h+1)
            for c in range(1, w+1)
            if (r, c) not in forbidden
        ]
        
        # 确定实际黑格数量
        max_possible = min(len(all_cells), self.max_black)
        n = random.randint(0, max_possible)
        black_cells = random.sample(all_cells, n) if n > 0 else []
        
        return {
            'h': h,
            'w': w,
            'n': n,
            'black_cells': sorted(black_cells, key=lambda x: (x[0], x[1]))
        }
    
    @staticmethod
    def prompt_func(question_case):
        h = question_case['h']
        w = question_case['w']
        n = question_case['n']
        cells = question_case['black_cells']
        
        problem = (
            "## Giant Chess Path Counting Problem\n\n"
            "### Background\n"
            "In Geraldion, a special chess variant is played on an h×w grid. The pawn starts at the top-left corner (1,1) "
            "and must reach the bottom-right corner ({h},{w}). The pawn can only move right or down, and cannot step on "
            "black cells. Your task is to calculate the number of valid paths modulo 10^9+7.\n\n"
            "### Problem Instance\n"
            "- Grid dimensions: {h} rows × {w} columns\n"
            "- Black cells: {n}\n".format(h=h, w=w, n=n)
        )
        
        if n > 0:
            problem += "- Coordinates of black cells:\n"
            for r, c in cells:
                problem += f"  ({r}, {c})\n"
        
        problem += (
            "\n### Answer Requirements\n"
            "Calculate the number of valid paths modulo 10^9+7.\n"
            "Enclose your final answer within [answer] tags like: [answer]12345[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

