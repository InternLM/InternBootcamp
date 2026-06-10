import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re




class KorpuzzlewordscapesInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlewordscapes Bootcamp指令生成器"""
    
    def __init__(self, min_size=3, max_size=6):
        """
        初始化Korpuzzlewordscapes指令生成器
        
        Args:
            min_size: 参数描述
            max_size: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_size = min_size
        self.max_size = max_size
    
    def case_generator(self):
        # 生成保证合法尺寸的网格
        rows = random.randint(max(3, self.min_size), self.max_size)
        cols = random.randint(max(3, self.min_size), self.max_size)
        
        def generate_valid_puzzle():
            while True:
                # 生成主横向单词
                main_word = random.choice(['CAT', 'DOG', 'CAR', 'BAT', 'ANT', 'OWL', 'BEE'])
                max_start_col = cols - len(main_word)
                if max_start_col < 0: continue
                start_col = random.randint(0, max_start_col)
                start_row = random.randint(0, rows-1)
                
                # 创建初始网格
                grid = [['0' for _ in range(cols)] for _ in range(rows)]
                for i in range(len(main_word)):
                    grid[start_row][start_col+i] = 'X'
                
                # 计算纵向单词的可行长度
                cross_pos = random.randint(0, len(main_word)-1)
                max_down_length = min(
                    start_row + 1,  # 向上可扩展空间
                    rows - start_row  # 向下可扩展空间
                )
                if max_down_length < 2: continue
                
                # 生成纵向单词（确保包含交叉字母）
                vertical_word = main_word[cross_pos] + ''.join(
                    random.choice(string.ascii_uppercase) 
                    for _ in range(max_down_length-1)
                )
                
                # 检查纵向单词布局的合法性
                valid = True
                vertical_length = len(vertical_word)
                for i in range(vertical_length):
                    r = start_row - cross_pos + i
                    if r < 0 or r >= rows:
                        valid = False
                        break
                    if grid[r][start_col + cross_pos] == 'X' and i != cross_pos:
                        valid = False
                if not valid: continue
                
                # 更新网格布局
                for i in range(vertical_length):
                    r = start_row - cross_pos + i
                    grid[r][start_col + cross_pos] = 'X'
                
                return {
                    "grid": grid,
                    "across": [main_word],
                    "down": [vertical_word],
                    "__solution__": self._generate_solution(
                        grid, main_word, vertical_word, 
                        start_row, start_col, cross_pos
                    )
                }

        return generate_valid_puzzle()
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case["grid"]
        across = question_case["across"]
        down = question_case["down"]
        
        grid_str = '\n'.join(' '.join(row) for row in grid)
        return f"""Solve this crossword puzzle:
- Grid layout (X=fillable, 0=blocked):
{grid_str}

Word lists:
- Across: {', '.join(across)}
- Down: {', '.join(down)}

Format your answer as space-separated values per row, comma-separated rows enclosed in double square brackets.
Example: [[A B 0, 0 C D]]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_solution(self, grid, across_word, down_word, start_row, start_col, cross_pos):
        solution = []
        for row in grid:
            solution.append(['0' if cell == '0' else '_' for cell in row])

        # 填充横向单词
        for i, c in enumerate(across_word):
            solution[start_row][start_col+i] = c

        # 填充纵向单词
        vertical_start_row = start_row - cross_pos
        for i, c in enumerate(down_word):
            r = vertical_start_row + i
            solution[r][start_col + cross_pos] = c

        return solution
