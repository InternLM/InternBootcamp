import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
from math import gcd




class CfadiandlcmInstructionGenerator(BaseInstructionGenerator):
    """Cfadiandlcm Bootcamp指令生成器"""
    
    def __init__(self, min_X=1, max_X=10**6):
        """
        初始化Cfadiandlcm指令生成器
        
        Args:
            min_X: 参数描述
            max_X: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_X = min_X
        self.max_X = max_X
    
    def case_generator(self):
        # 增加特殊案例生成逻辑
        if random.random() < 0.3:  # 30%概率生成边界案例
            candidates = [
                1,  # 最小边界
                random.choice([2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]),  # 小质数
                int(math.sqrt(self.max_X))**2,  # 最大平方数
                2**random.randint(1, 20),  # 2的幂次方
                2 * 3  # 两个质数的乘积
            ]
            X = random.choice(candidates)
            X = max(self.min_X, min(X, self.max_X))
        else:
            X = random.randint(self.min_X, self.max_X)
        return {'X': X}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        X = question_case['X']
        prompt = f"""Given X = {X}, find two positive integers a and b such that:
1. LCM(a, b) = X
2. max(a, b) is minimized

Output format: [answer]a b[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

