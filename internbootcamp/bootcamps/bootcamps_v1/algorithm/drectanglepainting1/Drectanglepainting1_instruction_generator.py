import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class Drectanglepainting1InstructionGenerator(BaseInstructionGenerator):
    """Drectanglepainting1 Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, black_prob=0.3):
        """
        初始化Drectanglepainting1指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            black_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.black_prob = black_prob
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        max_attempts = 100
        
        for _ in range(max_attempts):
            grid = [
                ''.join('#' if random.random() < self.black_prob else '.' 
                       for _ in range(n))
                for _ in range(n)
            ]
            black_count = sum(row.count('#') for row in grid)
            
            # 允许生成全白或包含黑块的case
            if black_count == 0 or any('#' in row for row in grid):
                break
        else:  # 多次尝试失败后生成全白网格
            grid = ['.'*n for _ in range(n)]
        
        min_cost = self.compute_min_cost(n, grid)
        return {'n': n, 'grid': grid, 'min_cost': min_cost}
    
    @staticmethod
    def prompt_func(question_case):
        problem_desc = [
            "你将得到一个n×n的网格，其中#表示黑色单元格，.表示白色单元格。",
            "每次操作可以选择任意矩形区域将其全部变为白色，费用为该矩形的高度和宽度中的较大值。",
            "请计算将所有黑色单元格变为白色的最小总费用。",
            "",
            "输入格式：",
            f"第一行：{question_case['n']}",
            "接下来n行：每行包含n个字符",
            "",
            "当前问题：",
            str(question_case['n'])
        ]
        problem_desc.extend(question_case['grid'])
        problem_desc.append(
            "\n请将最终答案放在[answer]和[/answer]标记之间，例如：[answer]5[/answer]"
        )
        return '\n'.join(problem_desc) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_cost(n, grid):
        # 初始化前缀和数组（从1开始索引）
        f = [[0]*(n+2) for _ in range(n+2)]
        for i in range(1, n+1):
            for j in range(1, n+1):
                cell_value = 1 if grid[i-1][j-1] == '#' else 0
                f[i][j] = f[i-1][j] + f[i][j-1] - f[i-1][j-1] + cell_value

        # 初始化四维DP数组
        d = [[[[0]*(n+2) for _ in range(n+2)] 
             for __ in range(n+2)] 
             for ___ in range(n+2)]

        # 动态规划计算
        for i in range(n, 0, -1):
            for j in range(n, 0, -1):
                for ii in range(i, n+1):
                    for jj in range(j, n+1):
                        # 计算当前区域的黑块总数
                        total = f[ii][jj] - f[i-1][jj] - f[ii][j-1] + f[i-1][j-1]

                        if total == 0:
                            d[i][j][ii][jj] = 0
                            continue

                        # 初始值为区域的最大边长
                        h = ii - i + 1
                        w = jj - j + 1
                        val = max(h, w)

                        # 垂直切分尝试
                        for k in range(j, jj):
                            val = min(val, d[i][j][ii][k] + d[i][k+1][ii][jj])

                        # 水平切分尝试
                        for k in range(i, ii):
                            val = min(val, d[i][j][k][jj] + d[k+1][j][ii][jj])

                        d[i][j][ii][jj] = val

        return d[1][1][n][n]
