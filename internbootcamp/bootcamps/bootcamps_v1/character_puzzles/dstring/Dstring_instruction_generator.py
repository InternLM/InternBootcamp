import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import heapq




class DstringInstructionGenerator(BaseInstructionGenerator):
    """Dstring Bootcamp指令生成器"""
    
    def __init__(self, s_len_min=3, s_len_max=10, k_min=1, k_max=100):
        """
        初始化Dstring指令生成器
        
        Args:
            s_len_min: 参数描述
            s_len_max: 参数描述
            k_min: 参数描述
            k_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.s_len_min = s_len_min
        self.s_len_max = s_len_max
        self.k_min = k_min
        self.k_max = k_max
    
    def case_generator(self):
        n = random.randint(self.s_len_min, self.s_len_max)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        total = n * (n + 1) // 2
        # Ensure k does not exceed the total number of substrings
        k = random.randint(self.k_min, min(self.k_max, total))
        return {
            's': s,
            'k': k
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        k = question_case['k']
        prompt = f"Anna and Maria are given the string: {s}\n"
        prompt += f"They need to find the {k}-th lexicographically smallest substring. "
        prompt += "All possible substrings, including duplicates, should be considered and sorted in lex order. "
        prompt += "If the total number of substrings is less than {k}, output 'No such line.' "
        prompt += "Please provide your answer within [answer] and [/answer] tags."
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

