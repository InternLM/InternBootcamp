import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class SkyscrapersInstructionGenerator(BaseInstructionGenerator):
    """Skyscrapers Bootcamp指令生成器"""
    
    def __init__(self, n=4):
        """
        初始化Skyscrapers指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        n = self.n
        square = self.generate_latin_square(n)
        clues = {
            'left': [],
            'right': [],
            'top': [],
            'bottom': []
        }
        
        for row in square:
            clues['left'].append(self.compute_view(row))
            clues['right'].append(self.compute_view(row[::-1]))
        
        for j in range(n):
            column = [square[i][j] for i in range(n)]
            clues['top'].append(self.compute_view(column))
            clues['bottom'].append(self.compute_view(column[::-1]))
        
        return {'n': n, 'clues': clues}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        clues = question_case['clues']
        example = "\n".join([" ".join(['1'] * n)] * n)
        prompt = (
            "你正在解决一个数织谜题（Skyscrapers Puzzle）。规则如下：\n"
            "1. 在{}×{}网格中填入1至{}，每行每列数字不重复。\n"
            "2. 周围数字表示从该方向能看到的摩天大楼数量（较高建筑会遮挡后面较矮的）。\n\n"
            "谜题线索：\n"
            "- 网格大小：{}×{}\n"
            "- 顶部线索（各列从上至下可见数）：{}\n"
            "- 底部线索（各列从下至上可见数）：{}\n"
            "- 左侧线索（各行从左至右可见数）：{}\n"
            "- 右侧线索（各行从右至左可见数）：{}\n\n"
            "请填入符合要求的网格，并将答案放在[answer]和[/answer]之间。格式示例：\n"
            "[answer]\n{}[/answer]"
        ).format(
            n, n, n, n, n,
            ' '.join(map(str, clues['top'])),
            ' '.join(map(str, clues['bottom'])),
            ' '.join(map(str, clues['left'])),
            ' '.join(map(str, clues['right'])),
            example
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_latin_square(n):
        square = []
        for i in range(n):
            row = [(i + j) % n + 1 for j in range(n)]
            square.append(row)
        random.shuffle(square)
        square = list(map(list, zip(*square)))
        random.shuffle(square)
        square = list(map(list, zip(*square)))
        return square

    @staticmethod
    def compute_view(view):
        max_h = -1
        count = 0
        for h in view:
            if h > max_h:
                count += 1
                max_h = h
        return count
