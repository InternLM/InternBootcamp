import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from typing import Dict
from typing import Any




class CinnaanddimaInstructionGenerator(BaseInstructionGenerator):
    """Cinnaanddima Bootcamp指令生成器"""
    
    def __init__(self, n: int = 5, m: int = 5):
        """
        初始化Cinnaanddima指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
    
    def case_generator(self) -> Dict[str, Any]:
        grid = []
        for _ in range(self.n):
            row = []
            for _ in range(self.m):
                row.append(random.choice(['D', 'I', 'M', 'A']))
            grid.append(''.join(row))
        return {
            'n': self.n,
            'm': self.m,
            'grid': grid
        }
    
    @staticmethod
    def prompt_func(question_case: Dict[str, Any]) -> str:
        grid = question_case['grid']
        n = question_case['n']
        m = question_case['m']
        prompt = f"给定一个{n}行{m}列的表格，如下所示：\n"
        for row in grid:
            prompt += f"行：{row}\n"
        prompt += "\n"
        prompt += "Inna希望尽可能多地走Cinnaanddima的循环。规则如下：\n"
        prompt += "1. Inna从一个D点开始。\n"
        prompt += "2. 每一步必须移动到相邻的格子（上下左右），且下一个字母必须是下一个字母（D→I→M→A→D）。\n"
        prompt += "3. 计算Inna能走多少次完整的Cinnaanddima循环。\n"
        prompt += "\n"
        prompt += "输出要求：\n"
        prompt += "如果Inna无法完成一次Cinnaanddima循环，输出“Poor Dima!”。\n"
        prompt += "如果存在无限循环的情况，输出“Poor Inna!”。\n"
        prompt += "否则，输出最大次数。\n"
        prompt += "\n"
        prompt += "请将答案放在[answer]标签中，例如：\n"
        prompt += "[answer]4[/answer]\n"
        prompt += "或者\n"
        prompt += "[answer]Poor Dima![/answer]\n"
        prompt += "或者\n"
        prompt += "[answer]Poor Inna![/answer]\n"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _compute_correct_answer(cls, grid: list, n: int, m: int) -> str:
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        dp = [[0 for _ in range(m)] for __ in range(n)]
        visited = [[False for _ in range(m)] for __ in range(n)]
        in_cycle = [[False for _ in range(m)] for __ in range(n)]
        has_infinite = False

        def next_char(c: str) -> str:
            if c == 'D':
                return 'I'
            elif c == 'I':
                return 'M'
            elif c == 'M':
                return 'A'
            else:
                return 'D'

        for i in range(n):
            for j in range(m):
                if grid[i][j] == 'D' and not visited[i][j]:
                    stack = [(i, j, 0, [])]
                    visited[i][j] = True
                    while stack:
                        x, y, steps, path = stack.pop()
                        if (x, y) in path:
                            has_infinite = True
                            break
                        new_path = path + [(x, y)]
                        current_char = grid[x][y]
                        next_c = next_char(current_char)
                        for dx, dy in directions:
                            nx = x + dx
                            ny = y + dy
                            if 0 <= nx < n and 0 <= ny < m:
                                if grid[nx][ny] == next_c and not visited[nx][ny]:
                                    visited[nx][ny] = True
                                    stack.append((nx, ny, steps + 1, new_path))
                        dp[x][y] = max(dp[x][y], steps // 4 + 1)
                    visited[i][j] = False
                    if has_infinite:
                        break
            if has_infinite:
                break

        if has_infinite:
            return "Poor Inna!"
        else:
            max_dima = 0
            for i in range(n):
                for j in range(m):
                    if dp[i][j] > max_dima:
                        max_dima = dp[i][j]
            if max_dima < 4:
                return "Poor Dima!"
            else:
                return str(max_dima // 4)
