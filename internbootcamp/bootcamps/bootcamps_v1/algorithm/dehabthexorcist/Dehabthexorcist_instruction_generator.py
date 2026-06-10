import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DehabthexorcistInstructionGenerator(BaseInstructionGenerator):
    """Dehabthexorcist Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dehabthexorcist指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
    
    def case_generator(self):
        case_type = random.choice([0, 1, 2, 3, 4, 5])
        u = 0
        v = 0

        if case_type == 0:
            u = 0
            v = 0
        elif case_type == 1:
            u = random.randint(1, 10**18)
            v = u
        elif case_type == 2:
            while True:
                x = random.randint(1, (10**18 - 1) // 2)
                max_u = 10**18 - 2 * x
                if max_u < 0:
                    continue
                k = x.bit_length()
                upper_limit = max_u >> k
                if upper_limit == 0:
                    u = 0
                else:
                    upper = random.randint(0, upper_limit)
                    u = upper << k
                if u <= max_u:
                    break
            v = u + 2 * x
        elif case_type == 3:
            while True:
                x = random.randint(1, (10**18 - 1) // 2)
                max_u = 10**18 - 2 * x
                if max_u < 1:
                    continue
                u = random.randint(1, max_u)
                if (x & u) != 0:
                    break
            v = u + 2 * x
        elif case_type == 4:
            v = random.randint(0, 10**18 - 1)
            delta = random.randint(1, 10**18 - v)
            u = v + delta
        elif case_type == 5:
            u = random.randint(0, 10**18)
            v = random.randint(0, 10**18)
            if (u % 2) == (v % 2):
                v += 1
                if v > 10**18:
                    v = u - 1 if u > 0 else 1

        return {'u': u, 'v': v}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        u = question_case['u']
        v = question_case['v']
        prompt = f"""You are given two integers u and v. Your task is to find the shortest possible array of positive integers such that the bitwise XOR of all its elements equals {u}, and the sum of all elements equals {v}. If no such array exists, output -1.

Input:
u = {u}, v = {v}

Output Format:
If no solution exists, output -1. Otherwise, output the length of the array followed by the array elements. If there are multiple valid answers, output any.

Examples:

Example 1:
Input: u=2, v=4
Output:
2
3 1

Example 2:
Input: u=1, v=3
Output:
3
1 1 1

Please provide your answer within [answer] and [/answer]. For example:

[answer]
2
3 1
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

