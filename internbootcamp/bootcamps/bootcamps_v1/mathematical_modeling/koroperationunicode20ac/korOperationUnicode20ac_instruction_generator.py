import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
import math
import ast




class Koroperationunicode20acInstructionGenerator(BaseInstructionGenerator):
    """Koroperationunicode20ac Bootcamp指令生成器"""
    
    def __init__(self, matrix_shape=(2,2), min_val=-10, max_val=10):
        """
        初始化Koroperationunicode20ac指令生成器
        
        Args:
            matrix_shape: 参数描述
            min_val: 参数描述
            max_val: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if not (len(matrix_shape) == 2 
                and all(isinstance(d, int) and d > 0 for d in matrix_shape)):
            raise ValueError("matrix_shape must be a tuple of two positive integers")
        if min_val > max_val:
            raise ValueError("min_val must be <= max_val")
        self.matrix_shape = matrix_shape
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        rows, cols = self.matrix_shape
        return {
            'A': [[random.randint(self.min_val, self.max_val) for _ in range(cols)] 
                  for _ in range(rows)],
            'B': [[random.randint(self.min_val, self.max_val) for _ in range(cols)] 
                  for _ in range(rows)]
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        def matrix_to_latex(matrix):
            return '\\[\n\\begin{pmatrix}\n' + ' \\\\\n'.join(
                '  ' + ' & '.join(map(str, row)) for row in matrix
            ) + '\n\\end{pmatrix}\n\\]'
        
        rows = len(question_case['A'])
        cols = len(question_case['A'][0]) if rows else 0
        
        # 修正示例格式生成逻辑
        example_rows = [
            '(' + ','.join(['...']*cols) + ')' 
            for _ in range(rows)
        ]
        format_example = f'[[({",".join(example_rows)})]]'
        
        return f"""请计算矩阵运算A€B=2A+3B，其中：

矩阵A：
{matrix_to_latex(question_case['A'])}

矩阵B：
{matrix_to_latex(question_case['B'])}

答案应为{rows}x{cols}矩阵。按照格式要求将最终答案置于双括号内：
示例格式：{format_example}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

