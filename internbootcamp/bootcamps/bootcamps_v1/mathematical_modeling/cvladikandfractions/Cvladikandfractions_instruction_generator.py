import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CvladikandfractionsInstructionGenerator(BaseInstructionGenerator):
    """Cvladikandfractions Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cvladikandfractions指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)  # 显式调用基类初始化
        self.max_n = params.get('max_n', 10000)  # 默认上限为10^4
    
    def case_generator(self):
        # 生成n的范围为1到max_n，包含所有可能的问题实例
        # 当n=1时答案应为-1，其他n≥2根据题目逻辑应有解
        n = random.randint(1, self.max_n)
        return {"n": n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case["n"]
        problem_text = (
            f"Vladik and Chloe are determining who is better at math. Vladik claims that for any positive integer n, "
            f"the fraction 2/n can be expressed as the sum of three distinct positive unit fractions. Help Vladik prove this "
            f"by finding three distinct positive integers x, y, z such that 1/x + 1/y + 1/z = 2/{n}. The numbers x, y, z must "
            f"not exceed 1e9. If it's impossible, output -1.\n\n"
            "Provide your answer as three space-separated integers or -1 enclosed within [answer] and [/answer] tags. "
            "Example: [answer]2 7 42[/answer] or [answer]-1[/answer] if no solution exists."
        )
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

