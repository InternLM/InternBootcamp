import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DandorandsquaresumInstructionGenerator(BaseInstructionGenerator):
    """Dandorandsquaresum Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100, max_bits=20):
        """
        初始化Dandorandsquaresum指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            max_bits: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = max(1, min_n)
        self.max_n = min(max_n, 200000)  # 安全限制
        self.max_bits = min(max_bits, 20)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        a = [
            random.randint(0, (1 << self.max_bits) - 1)
            for _ in range(n)
        ]
        # 确保至少一个案例全零
        if random.random() < 0.05:
            a = [0]*n
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        return f"""给定n={question_case['n']}个整数：{a_str}。通过任意次操作（选择i,j，设x=a_i,y=a_j，a_i变x&y，a_j变x|y），求最大平方和。答案写在[answer]标签内。例：[answer]0[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

