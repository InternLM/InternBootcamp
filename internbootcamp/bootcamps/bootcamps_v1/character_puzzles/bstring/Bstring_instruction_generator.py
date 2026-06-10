import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from heapq import heappush
from heapq import heappop
from heapq import heapify




class BstringInstructionGenerator(BaseInstructionGenerator):
    """Bstring Bootcamp指令生成器"""
    
    def __init__(self, max_str_length=10, max_k=100000):
        """
        初始化Bstring指令生成器
        
        Args:
            max_str_length: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_str_length = max_str_length
        self.max_k = max_k
    
    def case_generator(self):
        # Generate random string (length >=1)
        length = random.randint(1, self.max_str_length)
        chars = [random.choice('abcdefghijklmnopqrstuvwxyz') for _ in range(length)]
        s = ''.join(chars)
        
        # Calculate total possible substrings
        total_substrings = length * (length + 1) // 2
        
        # Generate k with controlled distribution
        if random.random() < 0.7:  # 70% valid k
            k = random.randint(1, min(total_substrings, self.max_k))
        else:  # 30% invalid k
            k = random.randint(
                min(total_substrings + 1, self.max_k),
                self.max_k  # Ensure k never exceeds problem constraints
            )
        return {'s': s, 'k': k}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        k = question_case['k']
        prompt = (
            f"In an IT lesson, Anna and Maria learned about lexicographic order. Their homework is to find the k-th lexicographically smallest substring of a given string.\n\n"
            f"**Rules:**\n"
            f"1. All possible contiguous substrings are considered (including duplicates from different starting positions). For example, 'aa' has substrings: 'a'(pos0), 'a'(pos1), 'aa'.\n"
            f"2. Substrings are ordered lexicographically as defined by the '<' operator.\n"
            f"3. If there are fewer than k substrings, output \"No such line.\"\n\n"
            f"**Input:**\nString: {s}\nk: {k}\n\n"
            f"**Task:**\nOutput the k-th substring. Enclose your answer in [answer][/answer] tags.\n\n"
            f"**Example:**\nInput: aa\nk=2\nAnswer: [answer]a[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

