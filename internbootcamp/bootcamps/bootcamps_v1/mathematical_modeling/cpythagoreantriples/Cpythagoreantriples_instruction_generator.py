import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CpythagoreantriplesInstructionGenerator(BaseInstructionGenerator):
    """Cpythagoreantriples Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10**9, allow_hypotenuse=True, **params):
        """
        初始化Cpythagoreantriples指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            allow_hypotenuse: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.allow_hypotenuse = allow_hypotenuse
        super().__init__(**params)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        leg_case = self.generate_leg_case(n)
        if leg_case:
            return {'n': n, 'm': leg_case[0], 'k': leg_case[1]}
        if self.allow_hypotenuse:
            hypotenuse_case = self.generate_hypotenuse_case(n)
            if hypotenuse_case:
                return {'n': n, 'm': hypotenuse_case[0], 'k': hypotenuse_case[1]}
        return {'n': n, 'solution': -1}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        solution = question_case.get('solution', None)
        example = "例如，当n=3时，输出4 5，因为3²+4²=5²。当n=6时，输出8 10，因为6²+8²=10²。"
        if solution == -1:
            example = "例如，当n=1时，无解，输出-1。"
        prompt = (
            f"Katya最近在学习毕达哥拉斯定理。她想知道，给定一个整数{n}，是否存在一个毕达哥拉斯三元组，其中n可以是直角边或斜边。"
            f"请找出这样的两个正整数m和k，使得n、m、k构成一个毕达哥拉斯三元组。如果没有这样的解，请输出-1。{example}"
            f"请输出答案，将答案放在[answer]标签中。"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_leg_case(n):
        if n == 1:
            return None
        if n % 2 == 1:
            m = (n**2 - 1) // 2
            k = m + 1
            if m > 0 and k > 0:
                return (m, k)
            return None
        else:
            m = (n**2 // 4) - 1
            k = m + 2
            if m > 0 and k > 0:
                return (m, k)
            return None

    @staticmethod
    def generate_hypotenuse_case(n):
        max_m = int((n**2)**0.5)
        for m in range(1, max_m):
            k_squared = n**2 - m**2
            if k_squared <= 0:
                continue
            k = int(k_squared**0.5)
            if k * k == k_squared and k > 0 and m < n and k < n:
                return (m, k)
        return None
