import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpolycarpusdiceInstructionGenerator(BaseInstructionGenerator):
    """Cpolycarpusdice Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_d=10, **params):
        """
        初始化Cpolycarpusdice指令生成器
        
        Args:
            max_n: 参数描述
            max_d: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化骰子谜题训练场参数
        :param max_n: 最大骰子数量，默认5
        :param max_d: 单个骰子最大面数，默认10
        """
        super().__init__(**params)  # 关键修复：显式调用父类初始化
        self.max_n = max_n
        self.max_d = max_d
    
    def case_generator(self):
        """
        生成有效的谜题实例
        返回包含n, A, d的字典
        """
        n = random.randint(1, self.max_n)
        d = [random.randint(1, self.max_d) for _ in range(n)]
        sum_d = sum(d)
        A = random.randint(n, sum_d)
        return {'n': n, 'A': A, 'd': d}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = f"{question_case['n']} {question_case['A']}\n{' '.join(map(str, question_case['d']))}"
        return f"""Polycarp has rolled some dice and now needs your help to determine impossible values. 

**Problem Statement:**
Given n dice where each dice i can show numbers between 1 and d_i, and the total sum is A, find for each dice how many numbers it **could not possibly** have shown based on these constraints.

**Input Format:**
- First line: n and A (space separated)
- Second line: d_1 d_2 ... d_n (space separated)

**Output Format:**
- n space-separated integers indicating the count of impossible values for each dice

**Example Input/Output:**
Input:
2 8
4 4
Output:
3 3

**Your Task:**
Solve the following case and enclose your answer in [answer]...[/answer] tags.

Input:
{input_lines}

[answer]
Place your answer here (e.g., '1 2 3')
[/answer]
""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

