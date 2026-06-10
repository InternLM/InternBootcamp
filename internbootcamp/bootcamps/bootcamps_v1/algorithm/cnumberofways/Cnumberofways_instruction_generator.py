import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CnumberofwaysInstructionGenerator(BaseInstructionGenerator):
    """Cnumberofways Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, element_range=100):
        """
        初始化Cnumberofways指令生成器
        
        Args:
            max_n: 参数描述
            element_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.element_range = element_range
    
    def case_generator(self):
        while True:
            n = random.randint(1, self.max_n)
            # Generate array with exactly n elements
            a = [random.randint(-self.element_range, self.element_range) for _ in range(n)]
            total = sum(a)
            remainder = total % 3
            
            # Adjust last element to make total divisible by 3
            adjust_range = [
                x for x in range(-self.element_range, self.element_range + 1)
                if (total - a[-1] + x) % 3 == 0
            ]
            
            if adjust_range:
                a[-1] = random.choice(adjust_range)
                return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        prompt = (
            "You are given an array of integers and need to split it into three contiguous parts with equal sums. "
            "Find the number of valid ways to make such splits.\n\n"
            "**Rules:**\n"
            "1. The array must be split into three contiguous non-empty parts by choosing indices i and j where 2 ≤ i ≤ j ≤ n-1.\n"
            "2. All three parts must have the same sum.\n\n"
            "**Input Format:**\n"
            "- The first line contains an integer n (1 ≤ n ≤ 5*10^5), the array length.\n"
            "- The second line contains n integers a_1 to a_n (|a_i| ≤ 1e9).\n\n"
            "**Output:**\n"
            "A single integer representing the number of valid splits.\n\n"
            "**Example:**\n"
            "Input:\n5\n1 2 3 0 3\nOutput:\n2\n\n"
            "**Current Problem:**\n"
            f"n = {n}\n"
            f"Array: {a}\n\n"
            "Calculate the answer and put your final answer within [answer] and [/answer]."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve(n, a):
        if n < 3:
            return 0
        total = sum(a)
        if total % 3 != 0:
            return 0
        target = total // 3

        prefix = [0] * (n + 1)
        for i in range(n):
            prefix[i + 1] = prefix[i] + a[i]

        suffix_count = [0] * (n + 2)
        for i in range(n, 0, -1):
            suffix_count[i] = suffix_count[i + 1]
            if prefix[n] - prefix[i - 1] == target:
                suffix_count[i] += 1

        result = 0
        for i in range(1, n - 1):
            if prefix[i] == target:
                result += suffix_count[i + 2]

        return result
