import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class D2rpdandrapsheethardversionInstructionGenerator(BaseInstructionGenerator):
    """D2rpdandrapsheethardversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, k_min=2, k_max=100):
        """
        初始化D2rpdandrapsheethardversion指令生成器
        
        Args:
            max_n: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.k_min = k_min
        self.k_max = k_max
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        k = random.randint(self.k_min, self.k_max)
        x0 = random.randint(0, n - 1) if n > 0 else 0
        return {
            'n': n,
            'k': k,
            'x0': x0
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        prompt = f"""You are trying to hack into a secure system. The password is initially between 0 and {n-1} (inclusive). You can make up to {n} guesses. 

Each time you guess incorrectly, the password changes using the k-itwise XOR operation in base {k}. Specifically, if the current password is x and you guess y, the new password becomes z such that x ⊕_{k} z = y. 

The k-itwise XOR is computed by adding each corresponding pair of digits in base {k} and taking the result modulo {k}. 

Your task is to determine a sequence of guesses that will find the correct password within {n} attempts. Provide your guesses as a comma-separated list of integers within [answer] and [/answer]. For example: [answer]3,4,5[/answer].

Ensure each guess is an integer between 0 and 20000000."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def subtract_kits(a, b, k):
        def get_digits(num):
            digits = []
            if num == 0:
                return [0]
            while num > 0:
                digits.append(num % k)
                num = num // k
            return digits

        a_digits = get_digits(a)
        b_digits = get_digits(b)
        max_len = max(len(a_digits), len(b_digits))
        a_digits += [0] * (max_len - len(a_digits))
        b_digits += [0] * (max_len - len(b_digits))
        result_digits = [(ad - bd) % k for ad, bd in zip(a_digits, b_digits)]
        result = 0
        for i, d in enumerate(result_digits):
            result += d * (k ** i)
        return result
