import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpocketbookInstructionGenerator(BaseInstructionGenerator):
    """Cpocketbook Bootcamp指令生成器"""
    
    def __init__(self, n=2, m=3):
        """
        初始化Cpocketbook指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if n < 1 or m < 1:
            raise ValueError("n and m must be at least 1")
        self.n = n
        self.m = m
    
    def case_generator(self):
        names = [[] for _ in range(self.n)]
        s_k_list = []
        
        for k in range(self.m):
            max_possible = min(self.n, 26)
            s_k = random.randint(1, max_possible)
            s_k_list.append(s_k)
            chars = random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', s_k)
            
            for i in range(self.n):
                if i < s_k:
                    c = chars[i]
                else:
                    c = random.choice(chars)
                names[i].append(c)
        
        names = [''.join(lst) for lst in names]
        return {
            'n': self.n,
            'm': self.m,
            'names': names,
            's_k_list': s_k_list
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [f"{question_case['n']} {question_case['m']}"] + question_case['names']
        input_str = '\n'.join(input_lines)
        
        prompt = f"""You are participating in a programming competition. Solve the following puzzle based on the described rules.

Problem Description:
Vasya found his mother's pocket book with n names, each exactly m letters long. The names are numbered 1 to n. Vasya can perform the following operation any number of times: choose two names (i and j, where i < j) and a length k, then swap the first k letters between them. The goal is to determine how many distinct names can end up in position 1 after any number of such operations. The answer should be given modulo 1000000007 (1e9+7).

Rules and Notes:
1. Each swap operation can be performed any number of times, with any valid i, j, and k.
2. The result depends on the different possible characters that can appear in each position of the first name.
3. For each position, the number of possible characters is equal to the number of distinct characters in that position across all names. The total answer is the product of these counts for all positions, modulo 1e9+7.

Input Format:
- The first line contains two integers n and m.
- The next n lines each contain a string of m uppercase letters.

Your Task:
Compute the correct answer for the provided input and write it inside [answer] and [/answer] tags. For example, if the answer is 4, write [answer]4[/answer].

Input Provided:
{input_str}

Please provide your answer within the tags as described."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

