import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CelementexterminationInstructionGenerator(BaseInstructionGenerator):
    """Celementextermination Bootcamp指令生成器"""
    
    def __init__(self, min_length=2, max_length=10):
        """
        初始化Celementextermination指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        n = random.randint(self.min_length, self.max_length)
        a = list(range(1, n + 1))
        random.shuffle(a)
        expected_answer = 'YES' if self.check_solution(a.copy()) else 'NO'  # 修复1：使用副本保证原始数据不变
        return {
            'n': n,
            'array': a,
            'expected_answer': expected_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        problem_desc = (
            "You are given an array a of length n, which is a permutation of numbers from 1 to n. "
            "In each operation, you can choose an index i (1 ≤ i < n) where a_i < a_{{i+1}}, "
            "and remove either a_i or a_{{i+1}}. The goal is to determine if it's possible to reduce "
            "the array to a single element using these operations.\n\n"
            "Input format:\n"
            "- The first line contains n (array length)\n"
            "- The second line contains the array elements\n\n"
            "Output 'YES' or 'NO'.\n\n"
            "Your task:\n"
            "Test case:\n"
            "n = {n}\n"
            "array: {a}\n\n"
            "Put your final answer within [answer] and [/answer] tags."
        ).format(
            n=question_case['n'],
            a=' '.join(map(str, question_case['array']))
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def check_solution(a):
        n = len(a)
        if n == 1:
            return True

        # 修复2：修正循环终止条件（参考原题正确解法）
        max_val = a[-1]
        for i in reversed(range(n-1)):
            if a[i] < max_val:
                max_val = a[i]
            else:
                return False
        return True
