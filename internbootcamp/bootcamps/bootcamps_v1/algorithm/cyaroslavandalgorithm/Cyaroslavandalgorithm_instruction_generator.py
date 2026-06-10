import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CyaroslavandalgorithmInstructionGenerator(BaseInstructionGenerator):
    """Cyaroslavandalgorithm Bootcamp指令生成器"""
    
    def __init__(self, n=2, max_digits=25):
        """
        初始化Cyaroslavandalgorithm指令生成器
        
        Args:
            n: 参数描述
            max_digits: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = n
        self.max_digits = max_digits
    
    def case_generator(self):
        numbers = []
        for _ in range(self.n):
            if random.random() < 0.1:
                length = random.randint(1, self.max_digits)
                num_str = '9' * length
            else:
                length = random.randint(1, self.max_digits)
                first_digit = str(random.randint(1, 9))
                rest = ''.join(str(random.randint(0, 9)) for _ in range(length - 1))
                num_str = first_digit + rest
            numbers.append(num_str)
        return {'n': self.n, 'numbers': numbers}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        numbers = question_case['numbers']
        n = question_case['n']
        problem = (
            "Yaroslav需要设计一个算法，该算法由一系列命令组成。每个命令的格式为si>>wi或si<>wi，其中si和wi是由数字和'?'组成的字符串，长度不超过7。算法的规则如下：\n\n"
            "1. 算法接收一个字符串作为输入a。\n"
            "2. 按命令顺序逐条检查，找到第一个si在a中出现的命令。\n"
            "3. 将a中第一个出现的si替换为wi。如果命令是si>>wi，则继续执行；如果命令是si<>wi，则终止。\n"
            "4. 算法必须在处理每个输入数字后，输出该数加一的结果。\n\n"
            f"给定{n}个数字，请设计符合条件的命令列表：\n"
        )
        for num in numbers:
            problem += f"{num}\n"
        problem += (
            "\n要求：\n"
            "- 每行一个命令，格式为si>>wi或si<>wi。\n"
            "- 命令数不超过50条。\n"
            "- 每个数字的处理必须在200次迭代内完成。\n"
            "将答案置于[answer]和[/answer]之间。"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def add_one(s):
        chars = list(s)
        carry = 1
        i = len(chars) - 1
        while i >= 0 and carry:
            digit = int(chars[i])
            new_digit = digit + carry
            if new_digit == 10:
                chars[i] = '0'
                carry = 1
            else:
                chars[i] = str(new_digit)
                carry = 0
            i -= 1
        if carry:
            chars = ['1'] + chars
        return ''.join(chars)

    @classmethod
    def apply_commands(cls, original, commands):
        a = original
        iterations = 0
        max_iter = 200
        while iterations < max_iter:
            found = False
            for si, op, wi in commands:
                pos = a.find(si)
                if pos != -1:
                    a = a[:pos] + wi + a[pos+len(si):]
                    iterations += 1
                    if op == '<>':
                        return a, iterations
                    else:
                        found = True
                        break
            if not found:
                break
        return a, iterations
