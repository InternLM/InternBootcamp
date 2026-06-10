import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict




class CcowandmessageInstructionGenerator(BaseInstructionGenerator):
    """Ccowandmessage Bootcamp指令生成器"""
    
    def __init__(self, min_length=3, max_length=10):
        """
        初始化Ccowandmessage指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        length = random.randint(self.min_length, self.max_length)
        chars = [random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length)]
        s = ''.join(chars)
        return {'s': s}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        return f"""Bessie the cow has intercepted the text string "{s}". A hidden message is a subsequence whose indices form an arithmetic progression. Two occurrences are distinct if they use different index sets. Your task is to find the maximum number of occurrences of any such hidden message.

For example, given "aaabb", the answer is 6 because "ab" appears 6 times.

Compute the answer for the given string and provide it as an integer within [answer] and [/answer]. For example: [answer]6[/answer].

Input string: {s}
Your answer:""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

