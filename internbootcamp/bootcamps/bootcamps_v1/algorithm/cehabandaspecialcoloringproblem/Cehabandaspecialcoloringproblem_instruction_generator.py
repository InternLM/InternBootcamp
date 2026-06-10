import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
from collections import defaultdict
from itertools import combinations
from math import gcd
import re




class CehabandaspecialcoloringproblemInstructionGenerator(BaseInstructionGenerator):
    """Cehabandaspecialcoloringproblem Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=100):
        """
        初始化Cehabandaspecialcoloringproblem指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        import random
        n = random.randint(self.min_n, self.max_n)
        return {'n': n}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        prompt = f"""You are given an integer n = {n}. Your task is to assign a positive integer a_i to each integer i from 2 to n such that the following conditions are met:

1. For every pair of coprime integers (i, j), a_i ≠ a_j.
2. The maximum value among all a_i is as small as possible.

Two integers are coprime if their greatest common divisor (GCD) is 1. Your solution should output the values a_2, a_3, ..., a_n separated by spaces.

Examples:

Input:
4
Output:
1 2 1

Input:
3
Output:
2 1

Your answer should include the sequence of numbers for a_2 to a_n enclosed within [answer] and [/answer] tags. For example, if your solution is "1 2 1" for n=4, write it as [answer]1 2 1[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

