import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from itertools import product




class KorpuzzlecampsiteInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlecampsite Bootcamp指令生成器"""
    
    def __init__(self, rows=5, cols=5):
        """
        初始化Korpuzzlecampsite指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        """生成具有唯一解的合法谜题案例"""
        n, m = self.rows, self.cols
        
        # 生成树和帐篷的合法布局
        while True:
            try:
                # 步骤1：生成随机树布局
                grid = [['X' for _ in range(m)] for _ in range(n)]
                for i in range(n):
                    j = random.choice(range(m))
                    grid[i][j] = 'T'
                
                # 步骤2：生成合法帐篷布局
                solution = [row.copy() for row in grid]
                tents = []
                # 为每个树尝试放置帐篷
                for i in range(n):
                    for j in range(m):
                        if grid[i][j] == 'T':
                            # 寻找可用相邻位置
                            adj_positions = []
                            for di, dj in [(-1,0),(1,0),(0,-1),(0,1)]:
                                ni, nj = i+di, j+dj
                                if 0<=ni<n and 0<=nj<m and solution[ni][nj] == 'X':
                                    adj_positions.append((ni, nj))
                            if adj_positions:
                                # 随机选择一个位置放置帐篷
                                ni, nj = random.choice(adj_positions)
                                solution[ni][nj] = 'C'
                                tents.append((ni, nj))
                                # 标记周围禁止帐篷
                                for dx in [-1,0,1]:
                                    for dy in [-1,0,1]:
                                        x, y = ni+dx, nj+dy
                                        if 0<=x<n and 0<=y<m and solution[x][y] == 'X':
                                            solution[x][y] = '.'
                # 清理占位符
                for i in range(n):
                    for j in range(m):
                        if solution[i][j] == '.':
                            solution[i][j] = 'X'
                
                # 计算约束条件
                row_clues = [row.count('C') for row in solution]
                col_clues = [sum(solution[i][j] == 'C' for i in range(n)) for j in range(m)]
                
                # 确保至少有一个帐篷且约束有效
                if sum(row_clues) == 0:
                    continue
                
                # 生成谜题网格（隐藏帐篷）
                puzzle_grid = [row.copy() for row in grid]
                return {
                    'grid': puzzle_grid,
                    'row_clues': row_clues,
                    'col_clues': col_clues,
                    'solution': solution
                }
            except:
                continue
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid = question_case['grid']
        row_clues = question_case['row_clues']
        col_clues = question_case['col_clues']
        n = len(grid)
        m = len(col_clues)
        
        # 构建网格表示
        grid_lines = []
        for i in range(n):
            row = '\t'.join(grid[i]) + '\t' + str(row_clues[i])
            grid_lines.append(row)
        
        # 添加列约束行
        col_line = '\t'.join(map(str, col_clues))
        grid_lines.append(col_line)
        
        # 构建完整提示
        prompt = f"""根据以下规则在{n}x{m}网格中放置帐篷：
1. 每个帐篷(C)必须与至少一棵树(T)正交相邻（上下左右）
2. 帐篷之间不能相邻（包括对角）
3. 行末数字表示该行需要的帐篷数
4. 最后一行数字表示各列需要的帐篷数

网格布局（T=树，X=空地）：
"""
        prompt += '\n'.join(grid_lines)
        prompt += "\n\n用C替换需要放置帐篷的X，保持T不变。答案格式：[[行元素 用 空格 分隔，行间用 逗号 分隔]]"
        prompt += "\n示例：[[T C X, X X T]]"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

