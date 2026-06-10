import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class NonogramsInstructionGenerator(BaseInstructionGenerator):
    """Nonograms Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Nonograms指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.rows = params.get('rows', 5)
        self.cols = params.get('cols', 5)
        self.fill_prob = params.get('fill_prob', 0.3)
    
    def case_generator(self):
        # Generate solution grid
        solution = [
            [random.random() < self.fill_prob for _ in range(self.cols)]
            for _ in range(self.rows)
        ]

        # Calculate clues
        rows_clues = [self._get_clues(row) for row in solution]
        cols_clues = [self._get_clues([solution[r][c] for r in range(self.rows)]) 
                     for c in range(self.cols)]

        return {'rows': rows_clues, 'columns': cols_clues}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        prompt = """你正在解决一个Nonogram谜题。根据行和列的数字线索填充网格：

规则说明：
1. 数字表示连续填充的单元格块，块间至少间隔一个空格
2. 行线索从左到右排列，列线索从上到下排列
3. 用'X'表示填充，用空格或'.'表示空白

行线索：
""" + "\n".join(
    f"第{i+1}行: {clues if clues else '无'}" 
    for i, clues in enumerate(question_case['rows'])
) + "\n\n列线索：\n" + "\n".join(
    f"第{i+1}列: {clues if clues else '无'}" 
    for i, clues in enumerate(question_case['columns'])
) + """

请将最终答案放在[answer]标签内，每行用'X'和空格表示填充状态：
示例：
[answer]
XX X
 XXX
X  X
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _get_clues(line):
        clues = []
        current = 0
        for cell in line:
            if cell:
                current += 1
            elif current > 0:
                clues.append(current)
                current = 0
        if current > 0:
            clues.append(current)
        return clues
