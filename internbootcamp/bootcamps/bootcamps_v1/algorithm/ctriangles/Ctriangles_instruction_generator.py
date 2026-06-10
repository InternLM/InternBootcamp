import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CtrianglesInstructionGenerator(BaseInstructionGenerator):
    """Ctriangles Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, **kwargs):
        """
        初始化Ctriangles指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        board = [''.join(random.choices('0123456789', k=n)) for _ in range(n)]
        expected = self.calculate_answer(n, board)
        return {'n': n, 'board': board, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        board = question_case['board']
        return (
            "你是一个编程竞赛选手，需要解决以下问题。\n\n"
            "问题描述：\n"
            "给定一个n×n的棋盘，每个单元格包含一个0-9的数字。对于每个数字d（0-9），你必须将恰好一个单元格的数值改为d，然后找出满足以下条件的最大三角形的面积的两倍：\n"
            "1. 三角形的三个顶点都是d。\n"
            "2. 至少有一条边与棋盘的边平行。\n\n"
            "输入格式：\n"
            f"n = {n}\n棋盘内容如下：\n" + "\n".join(board) + "\n\n"
            "输出格式：\n"
            "输出10个整数，分别对应d=0到d=9的结果，每个整数为最大面积的两倍。\n"
            "答案必须用[answer]和[/answer]标签包裹，例如：[answer]0 0 0 0 0 0 0 0 0 0[/answer]。"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_answer(n, board):
        ans = [0] * 10
        for d in range(10):
            min_row = max_row = min_col = max_col = None
            # Find original extents for d
            original_exists = False
            for i in range(n):
                for j in range(n):
                    if int(board[i][j]) == d:
                        if not original_exists:
                            min_row = max_row = i
                            min_col = max_col = j
                            original_exists = True
                        else:
                            min_row = min(min_row, i)
                            max_row = max(max_row, i)
                            min_col = min(min_col, j)
                            max_col = max(max_col, j)

            if not original_exists:
                # Must create one cell of d (area remains 0)
                ans[d] = 0
                continue

            max_area = (max_row - min_row) * (max_col - min_col)
            # Check all possible cell modifications
            for i in range(n):
                for j in range(n):
                    new_min_row = min(min_row, i)
                    new_max_row = max(max_row, i)
                    new_min_col = min(min_col, j)
                    new_max_col = max(max_col, j)
                    candidate = (new_max_row - new_min_row) * (new_max_col - new_min_col)
                    if candidate > max_area:
                        max_area = candidate
            ans[d] = max_area
        return ans
