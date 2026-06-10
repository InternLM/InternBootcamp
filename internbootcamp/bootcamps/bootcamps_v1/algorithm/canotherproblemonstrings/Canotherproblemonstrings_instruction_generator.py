import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CanotherproblemonstringsInstructionGenerator(BaseInstructionGenerator):
    """Canotherproblemonstrings Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Canotherproblemonstrings指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_s_length = params.get('min_s_length', 1)
        self.max_s_length = params.get('max_s_length', 20)
        self.min_k = params.get('min_k', 0)
        self.max_k = params.get('max_k', 20)
    
    def case_generator(self):
        s_length = random.randint(self.min_s_length, self.max_s_length)
        s = ''.join(random.choice('01') for _ in range(s_length))
        k = random.randint(self.min_k, self.max_k)
        return {"k": k, "s": s}
    
    @staticmethod
    def prompt_func(question_case):
        k = question_case['k']
        s = question_case['s']
        problem_desc = f"""
You are a programming competition contestant. Your task is to solve the following problem:

Given an integer k and a binary string s, find the number of substrings of s that contain exactly k '1' characters. A substring is a contiguous non-empty sequence of characters. Two substrings are considered different if they start or end at different positions, even if their contents are identical.

Input Format:
- The first line contains the integer k.
- The second line contains the binary string s.

Output Format:
- A single integer representing the number of valid substrings.

Example:
Input:
1
1010
Output:
6

Your Task:
The current problem instance has the following inputs:
k = {k}
s = "{s}"

Please compute the correct answer and enclose it within [answer] and [/answer] tags. For example, if the answer is 5, write it as [answer]5[/answer].
"""
        return problem_desc.strip() 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

