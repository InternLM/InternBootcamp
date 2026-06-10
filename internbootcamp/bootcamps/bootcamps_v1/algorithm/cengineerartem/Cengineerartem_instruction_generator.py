import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CengineerartemInstructionGenerator(BaseInstructionGenerator):
    """Cengineerartem Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, min_m=1, max_m=100, seed=None):
        """
        初始化Cengineerartem指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
        self.rng = random.Random(seed)
    
    def case_generator(self):
        n = self.rng.randint(self.min_n, self.max_n)
        m = self.rng.randint(self.min_m, self.max_m)
        
        # 确保生成的b矩阵满足奇偶棋盘模式
        b = []
        for i in range(n):
            row = []
            for j in range(m):
                base_value = self.rng.randint(1, 10**3)  # 缩小数值范围便于测试
                parity = (i + j) % 2
                if (base_value % 2) != parity:
                    base_value += 1
                row.append(base_value)
            b.append(row)
        
        # 生成对应的a矩阵（确保值不低于1）
        a = []
        for i in range(n):
            row_a = []
            for j in range(m):
                if self.rng.choice([True, False]) and b[i][j] > 1:
                    row_a.append(b[i][j] - 1)
                else:
                    row_a.append(b[i][j])
            a.append(row_a)
        
        return {
            'n': n,
            'm': m,
            'a': a,
            'expected_parity_pattern': [[(i+j)%2 for j in range(m)] for i in range(n)]  # 添加校验模式
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        matrix_str = '\n'.join(' '.join(map(str, row)) for row in question_case['a'])
        return f"""Artem需要调整一个矩阵使其相邻单元格不重复。每个单元格可以选择保持原值或+1。

当前矩阵（{question_case['n']}行×{question_case['m']}列）：
{matrix_str}

请输出修改后的矩阵，确保：
1. 相邻单元格（上下左右）的值不同
2. 每个单元格只能是原值或原值+1
3. 将最终答案用[answer]标签包裹，例如：
[answer]
1 2
3 4
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

