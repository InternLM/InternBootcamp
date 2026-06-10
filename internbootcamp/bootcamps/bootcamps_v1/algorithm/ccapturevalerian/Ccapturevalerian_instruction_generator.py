import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from string import digits




class CcapturevalerianInstructionGenerator(BaseInstructionGenerator):
    """Ccapturevalerian Bootcamp指令生成器"""
    
    def __init__(self, roman_prob=0.5, min_a=2, max_a=25, min_b=2, max_b=25):
        """
        初始化Ccapturevalerian指令生成器
        
        Args:
            roman_prob: 参数描述
            min_a: 参数描述
            max_a: 参数描述
            min_b: 参数描述
            max_b: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.roman_prob = roman_prob
        self.min_a = min_a
        self.max_a = max_a
        self.min_b = min_b
        self.max_b = max_b
    
    def case_generator(self):
        is_roman = random.random() < self.roman_prob
        if is_roman:
            a = random.randint(self.min_a, self.max_a)
            b = 'R'
            num = random.randint(1, 3999)
        else:
            a = random.randint(self.min_a, self.max_a)
            b = random.randint(self.min_b, self.max_b)
            num = random.randint(0, 101510)
        
        # 生成基数转换并添加前导零
        c = self.decimal_to_base(num, a)
        max_leading = 1000 - len(c)  # 题目限制长度为10^3
        leading_zeros = random.randint(0, max_leading) if max_leading > 0 else 0
        c = '0' * leading_zeros + c

        correct_answer = self.decimal_to_roman(num) if is_roman else self.decimal_to_base(num, b)
        return {
            'a': a,
            'b': b,
            'c': c,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        a = question_case['a']
        b = question_case['b']
        c = question_case['c']
        problem = (
            f"Convert the base-{a} number {c} to "
            f"{'Roman numerals' if b == 'R' else f'base {b}'}.\n\n"
            "Rules:\n"
            "- Input number may contain leading zeros\n"
            "- Roman numerals use subtractive notation (e.g., IV=4, IX=9)\n"
            "- Omit leading zeros in output except for zero value\n\n"
            "Put your final answer within [answer]...[/answer] tags."
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def decimal_to_base(n, base):
        if n == 0:
            return '0'
        digits = []
        while n > 0:
            remainder = n % base
            digits.append(str(remainder) if remainder < 10 else chr(ord('A') + remainder - 10))
            n = n // base
        return ''.join(reversed(digits)) if digits else '0'

    @staticmethod
    def decimal_to_roman(num):
        val = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4, 1
        ]
        syms = [
            "M", "CM", "D", "CD",
            "C", "XC", "L", "XL",
            "X", "IX", "V", "IV",
            "I"
        ]
        roman_num = []
        i = 0
        while num > 0:
            count = num // val[i]
            roman_num.append(syms[i] * count)
            num -= val[i] * count
            i += 1
        return ''.join(roman_num)
