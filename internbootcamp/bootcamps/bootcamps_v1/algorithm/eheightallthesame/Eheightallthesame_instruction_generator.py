import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EheightallthesameInstructionGenerator(BaseInstructionGenerator):
    """Eheightallthesame Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Eheightallthesame指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        # 允许生成n=1或m=1但保证n*m>=2的默认参数
        self.n_range = params.get('n_range', (1, 5))  
        self.m_range = params.get('m_range', (1, 5))
        self.L_min = params.get('L_min', 0)
        self.L_max = params.get('L_max', 5)
        self.R_min = params.get('R_min', 0)
        self.R_max = params.get('R_max', 10)
    
    def case_generator(self):
        # 确保生成合法网格尺寸的核心逻辑
        while True:
            n = random.randint(*self.n_range)
            m = random.randint(*self.m_range)
            if n * m >= 2:
                break
        
        # 生成合法L,R参数对
        L = random.randint(self.L_min, self.L_max)
        R = random.randint(max(L, self.R_min), self.R_max)
        
        return {
            'n': n,
            'm': m,
            'L': L,
            'R': R
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        params = {
            'n': question_case['n'],
            'm': question_case['m'],
            'L': question_case['L'],
            'R': question_case['R'],
            'cells': '×'.join([str(question_case['n']), str(question_case['m'])])
        }
        return (
            f"在Eheightallthesame游戏中，Alice面对一个{params['n']}行{params['m']}列的网格（共{params['cells']}格）。"
            f"每个单元格初始立方体数a_{{i,j}}满足{params['L']} ≤ a_{{i,j}} ≤ {params['R']}。\n\n"
            "合法操作：\n"
            "1. 选择两个相邻单元格各+1立方体\n"
            "2. 选择一个单元格+2立方体\n\n"
            "请求满足以下条件的初始配置总数（模998244353）：\n"
            "- 所有初始值在给定范围内\n"
            "- 通过操作可使所有单元格高度相同\n\n"
            "答案请用[answer]标签包裹，例如：[answer]12345[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

