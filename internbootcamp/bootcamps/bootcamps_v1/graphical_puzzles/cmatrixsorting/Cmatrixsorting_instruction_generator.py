import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from copy import deepcopy
from typing import List
from typing import Union




class CmatrixsortingInstructionGenerator(BaseInstructionGenerator):
    """Cmatrixsorting Bootcamp指令生成器"""
    
    def __init__(self, n: int = 3, m: int = 3, has_solution_prob: float = 0.5):
        """
        初始化Cmatrixsorting指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
            has_solution_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.m = m
        self.has_solution_prob = has_solution_prob
    
    def case_generator(self) -> dict:
        if random.random() < self.has_solution_prob:
            A = self._generate_matrix()
            cols = self._generate_sorting_columns()
            B = self._apply_sorting(A, cols)
            return {
                'n': self.n,
                'm': self.m,
                'A': A,
                'B': B,
                'has_solution': True
            }
        else:
            A = self._generate_matrix()
            cols = self._generate_sorting_columns()
            B = self._apply_sorting(A, cols)
            B = self._corrupt_matrix(A, B)
            return {
                'n': self.n,
                'm': self.m,
                'A': A,
                'B': B,
                'has_solution': False
            }
    
    @staticmethod
    def prompt_func(question_case: dict) -> str:  # 修正参数名称为question_case
        n = question_case['n']
        m = question_case['m']  # 正确获取表格尺寸参数
        prompt = f"""给定两个{n}x{m}表格A和B：
        
表A：
"""
        prompt += '\n'.join(' '.join(map(str, row)) for row in question_case['A'])
        prompt += "\n\n表B：\n"
        prompt += '\n'.join(' '.join(map(str, row)) for row in question_case['B'])
        prompt += "\n\n是否可通过列排序转换？答案格式：\n- 无解：[answer]-1[/answer]\n- 有解：[answer]列序列[/answer] (如[answer]1 2 3[/answer])"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_matrix(self):
        return [[random.randint(1, self.n) for _ in range(self.m)] 
                for _ in range(self.n)]

    def _generate_sorting_columns(self):
        return random.choices(range(1, self.m+1), 
                            k=random.randint(0, self.m))

    def _apply_sorting(self, matrix, columns):
        sorted_mat = deepcopy(matrix)
        for col in columns:
            sorted_mat.sort(key=lambda row: row[col-1])
        return sorted_mat

    def _corrupt_matrix(self, A, B):  # 统一方法名称
        B_prime = deepcopy(B)
        A_rows = {tuple(row) for row in A}

        # 确保至少存在一个非法行
        for i in range(self.n):
            if tuple(B_prime[i]) not in A_rows:
                continue

            for j in range(self.m):
                for v in range(1, self.n+2):
                    new_row = list(B_prime[i])
                    new_row[j] = v
                    if tuple(new_row) not in A_rows:
                        B_prime[i] = new_row
                        return B_prime

        # 最终保护：随机生成全新行
        while True:
            new_row = [random.randint(1, self.n+1) for _ in range(self.m)]
            if tuple(new_row) not in A_rows:
                B_prime[random.randint(0, self.n-1)] = new_row
                return B_prime
