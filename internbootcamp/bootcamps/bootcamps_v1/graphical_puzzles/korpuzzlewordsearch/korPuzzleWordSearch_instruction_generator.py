import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class KorpuzzlewordsearchInstructionGenerator(BaseInstructionGenerator):
    """Korpuzzlewordsearch Bootcamp指令生成器"""
    
    def __init__(self, grid_size=13, word_list=None):
        """
        初始化Korpuzzlewordsearch指令生成器
        
        Args:
            grid_size: 参数描述
            word_list: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.grid_size = grid_size
        self.word_list = word_list or self._default_word_list()
    
    def case_generator(self):
        grid = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        directions = [
            (0, 1), (1, 0), (1, 1), (1, -1),
            (0, -1), (-1, 0), (-1, -1), (-1, 1)
        ]

        for word in self.word_list:
            word = word.upper()
            placed = False
            for _ in range(100):
                dr, dc = random.choice(directions)
                reverse = random.choice([True, False])
                current_word = word[::-1] if reverse else word
                length = len(current_word)

                max_row = self.grid_size - 1 - (length-1)*max(0, dr)
                min_row = (length-1)*abs(min(0, dr))
                max_col = self.grid_size - 1 - (length-1)*max(0, dc)
                min_col = (length-1)*abs(min(0, dc))

                if max_row < min_row or max_col < min_col:
                    continue

                row = random.randint(min_row, max_row)
                col = random.randint(min_col, max_col)

                valid = True
                positions = []
                for i in range(length):
                    r = row + i*dr
                    c = col + i*dc
                    if not (0 <= r < self.grid_size and 0 <= c < self.grid_size):
                        valid = False
                        break
                    existing = grid[r][c]
                    if existing and existing != current_word[i]:
                        valid = False
                        break
                    positions.append((r, c))
                
                if valid:
                    for i, (r, c) in enumerate(positions):
                        grid[r][c] = current_word[i]
                    placed = True
                    break
            if not placed:
                raise ValueError(f"Failed to place word: {word}")

        for i in range(self.grid_size):
            for j in range(self.grid_size):
                if grid[i][j] is None:
                    grid[i][j] = random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        return {
            "grid": [row.copy() for row in grid],
            "word_list": self.word_list.copy()
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        grid = question_case["grid"]
        word_list = question_case["word_list"]
        grid_lines = ["  ".join(row) for row in grid]
        grid_str = "\n".join(grid_lines)
        word_str = " ".join(word_list) + "."
        
        return f"""You are participating in a word search puzzle. Find all hidden words in the following grid. Words can be arranged horizontally, vertically, diagonally, forwards, or backwards.

Grid (rows and columns are 0-indexed from top-left):
{grid_str}

Word List:
{word_str}

Format your answer with each word's start and end coordinates like this:
WORD (start_row,start_col)(end_row,end_col)

List answers in the order of the word list, each on a new line. Enclose your final answer within double square brackets. Example:
[[EXAMPLE (0,0)(3,0)
WORDS (2,4)(2,8)]]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _default_word_list(self):
        return ["SAMPLE", "WORDS", "PUZZLE"]
