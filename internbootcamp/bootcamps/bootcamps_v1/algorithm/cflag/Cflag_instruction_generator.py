import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from string import ascii_lowercase




class CflagInstructionGenerator(BaseInstructionGenerator):
    """Cflag Bootcamp指令生成器"""
    
    def __init__(self, n=4, m=3):
        """
        初始化Cflag指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
    
    def case_generator(self):
        grid = []
        for _ in range(self.n):
            row = ''.join(random.choice(ascii_lowercase) for _ in range(self.m))
            grid.append(row)
        
        correct_answer = self._calculate_correct_answer(grid)
        return {
            'grid': grid,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case['grid']
        problem = (
            "Innokenty has a rectangular blanket divided into colored pieces. He wants to cut out subrectangles that form valid country flags. "
            "A valid flag must have three equal-height horizontal stripes, each with a uniform color, and adjacent stripes must have different colors. "
            "Your task is to count how many such subrectangles exist in the given blanket.\n\n"
            "The blanket is as follows:\n"
        )
        for i, row in enumerate(grid):
            problem += f"Row {i+1}: {row}\n"
        problem += (
            "Please provide the number of valid flag subrectangles in the format: [answer]X[/answer], where X is the count."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _calculate_correct_answer(cls, grid):
        n = len(grid)
        if n == 0:
            return 0
        m = len(grid[0])
        down = [[None] * m for _ in range(n)]

        for c in range(m):
            szs = []
            cnt = 1
            for r in range(1, n):
                if grid[r][c] == grid[r-1][c]:
                    cnt += 1
                else:
                    szs.append(cnt)
                    cnt = 1
            szs.append(cnt)

            st = 0
            for i in range(1, len(szs)-1):
                if szs[i] > min(szs[i-1], szs[i+1]):
                    st += szs[i-1]
                    continue
                sz = szs[i]
                top_start = st
                top_end = st + szs[i-1] - 1
                mid_start = top_end + 1
                mid_end = mid_start + sz - 1
                if mid_end >= n:
                    st += szs[i-1]
                    continue
                bot_start = mid_end + 1
                bot_end = bot_start + sz - 1
                if bot_end >= n:
                    st += szs[i-1]
                    continue
                top_color = grid[top_start][c]
                mid_color = grid[mid_start][c]
                bot_color = grid[bot_start][c]
                if top_color != mid_color and mid_color != bot_color:
                    for r in range(top_start, top_end + 1):
                        down[r][c] = (sz, top_color, mid_color, bot_color)
                st += szs[i-1]

        out = 0
        for r in range(n):
            st = 0
            cnt = 0
            cur = None
            while st < m:
                cell = down[r][st]
                if cell is None:
                    if cnt > 0:
                        out += (cnt + 1) * cnt // 2
                        cnt = 0
                    st += 1
                else:
                    if cell == cur:
                        cnt += 1
                    else:
                        if cnt > 0:
                            out += (cnt + 1) * cnt // 2
                        cur = cell
                        cnt = 1
                    st += 1
            if cnt > 0:
                out += (cnt + 1) * cnt // 2
        return out
