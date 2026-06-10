import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_answer(A, B, C, D):
    len_f = D - B + 2
    f = [0] * len_f

    for y in range(B, C + 1):
        start = C - y
        end = D - y + 1
        if start < len_f:
            f[start] += 1
        if end < len_f and end > 0:
            f[end] -= 1

    ans = f[0] * (B - A + 1)
    for d in range(1, B):
        if d >= len_f:
            break
        f[d] += f[d-1]
        current_min = min(B - A + 1, B - d)
        ans += f[d] * current_min

    return ans


class CcounttrianglesInstructionGenerator(BaseInstructionGenerator):
    """Ccounttriangles Bootcamp指令生成器"""
    
    def __init__(self, max_A=1000, max_step=1000):
        """
        初始化Ccounttriangles指令生成器
        
        Args:
            max_A: 参数描述
            max_step: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_A = min(max_A, 500000)
        self.max_step = min(max_step, 500000)
    
    def case_generator(self):
        MAX_LIMIT = 500000
        
        A = random.randint(1, self.max_A)
        B = random.randint(A, min(A + self.max_step, MAX_LIMIT))
        C = random.randint(B, min(B + self.max_step, MAX_LIMIT))
        D = random.randint(C, min(C + self.max_step, MAX_LIMIT))
        
        return {
            'A': A,
            'B': B,
            'C': C,
            'D': D,
            'correct_answer': calculate_answer(A, B, C, D)
        }
    
    @staticmethod
    def prompt_func(question_case):
        params = question_case
        return f"""Yuri最喜欢的四个数字满足A ≤ B ≤ C ≤ D。请计算满足以下条件的三元组(x, y, z)数量：
        
- {params['A']} ≤ x ≤ {params['B']}
- {params['B']} ≤ y ≤ {params['C']}
- {params['C']} ≤ z ≤ {params['D']}
- 构成非退化三角形（x + y > z）

答案请用[answer]标签包裹，例如：[answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

