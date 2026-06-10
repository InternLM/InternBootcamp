import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import ast




class KakurasuInstructionGenerator(BaseInstructionGenerator):
    """Kakurasu Bootcamp指令生成器"""
    
    def __init__(self, n=5):
        """
        初始化Kakurasu指令生成器
        
        Args:
            n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
    
    def case_generator(self):
        n = self.n
        grid = [[random.choice([0, 1]) for _ in range(n)] for _ in range(n)]
        
        row_targets = []
        for i in range(n):
            total = sum((j + 1) * cell for j, cell in enumerate(grid[i]))
            row_targets.append(total)
        
        col_targets = []
        for j in range(n):
            total = sum((i + 1) * grid[i][j] for i in range(n))
            col_targets.append(total)
        
        return {
            'n': n,
            'row_targets': row_targets,
            'col_targets': col_targets
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        row_targets = question_case['row_targets']
        col_targets = question_case['col_targets']
        return f"""你正在解决一个Kakurasu谜题。这是一个{n}x{n}的网格谜题，目标是根据行和列的约束条件涂黑单元格。

规则：
1. 每行中被涂黑单元格的列索引（从左到右为1到{n}）之和等于该行的目标值。
2. 每列中被涂黑单元格的行索引（从上到下为1到{n}）之和等于该列的目标值。
3. 每个单元格必须明确涂黑（1）或未涂黑（0）。

当前谜题的行目标值（从上到下）：{row_targets}
当前谜题的列目标值（从左到右）：{col_targets}

请将你的解答格式化为{n}x{n}的二维数组，其中1表示涂黑，0表示未涂黑，并用[answer]和[/answer]标签包裹。例如：
[answer]
[[1, 0, 0], [0, 1, 0], [0, 0, 1]]
[/answer]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

