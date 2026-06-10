import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from itertools import product




class KorpuzzleminesweeperInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzleminesweeper Bootcamp指令生成器"""
    
    def __init__(self, size=5, mine_ratio=0.15, min_hints=3):
        """
        初始化Korpuzzleminesweeper指令生成器
        
        Args:
            size: 参数描述
            mine_ratio: 参数描述
            min_hints: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.size = size
        self.mine_count = max(1, min(int(size*size*mine_ratio), size*size-2))
        self.min_hints = min_hints
        self.params = {
            'size': size,
            'mine_count': self.mine_count,
            'min_hints': min_hints
        }
    
    def case_generator(self):
        size = self.size
        while True:  # 确保生成有效谜题
            # 随机生成地雷布局
            mines = set()
            while len(mines) < self.mine_count:
                mines.add((random.randint(0, size-1), random.randint(0, size-1)))
            
            # 生成完整提示网格
            full_grid = []
            for r in range(size):
                row = []
                for c in range(size):
                    if (r,c) in mines:
                        row.append('X')
                    else:
                        count = sum(1 for dr,dc in product((-1,0,1), repeat=2)
                                   if (r+dr, c+dc) in mines and 0<=r+dr<size and 0<=c+dc<size)
                        row.append(str(count) if count>0 else '0')
                full_grid.append(row)
            
            # 选择需要保留的提示格（至少保留min_hints个非零提示）
            safe_cells = [(r,c) for r,c in product(range(size), repeat=2) 
                        if (r,c) not in mines and full_grid[r][c] != '0']
            if len(safe_cells) < self.min_hints:
                continue  # 重生成
            
            keep_hints = random.sample(safe_cells, k=random.randint(self.min_hints, len(safe_cells)))
            
            # 生成谜题网格
            puzzle_grid = []
            for r in range(size):
                puzzle_row = []
                for c in range(size):
                    if (r,c) in keep_hints or (r,c) in mines:
                        puzzle_row.append(full_grid[r][c])
                    else:
                        puzzle_row.append('X')
                puzzle_grid.append(puzzle_row)
            
            # 有效性检查：至少有一个可推断的确定位置
            if self.validate_puzzle(puzzle_grid, mines):
                return {
                    'grid': puzzle_grid,
                    'mines': list(mines),
                    'full_grid': full_grid
                }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid = question_case['grid']
        grid_str = "\n".join(["\t".join(row) for row in grid])
        return f"""扫雷谜题规则：
1. 数字表示周围8格中地雷的总数
2. X需要判断是否为地雷：是地雷改为A，不是则保持X
3. 现有数字和X的位置不可修改，只能改动X→A

当前谜题（{len(grid)}x{len(grid)}）：
{grid_str}

最终答案格式示例（每行用空格分隔，行间用逗号分隔）：
[[A X 2,X A 3,2 3 A]]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def validate_puzzle(puzzle_grid, mines):
        """至少存在一个可直接推断的确定位置"""
        size = len(puzzle_grid)
        for r in range(size):
            for c in range(size):
                if puzzle_grid[r][c] == 'X':
                    continue
                if puzzle_grid[r][c] == '0':
                    return True  # 0周围必无雷
                required = int(puzzle_grid[r][c])
                hidden = 0
                confirmed_mines = 0
                for dr, dc in product((-1,0,1), repeat=2):
                    nr, nc = r+dr, c+dc
                    if 0<=nr<size and 0<=nc<size:
                        if (nr, nc) in mines:
                            confirmed_mines +=1
                        elif puzzle_grid[nr][nc] == 'X':
                            hidden +=1
                if required == confirmed_mines and hidden >0:
                    return True  # 存在可标记的安全区域
        return False
