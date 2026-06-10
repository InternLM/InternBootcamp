import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import bisect




class FteodorisnotaliarInstructionGenerator(BaseInstructionGenerator):
    """Fteodorisnotaliar Bootcamp指令生成器"""
    
    def __init__(self, n=2, m=4):
        """
        初始化Fteodorisnotaliar指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Initialize the Fteodorisnotaliarbootcamp with parameters for number of segments and maximum coordinate.
        Default values are n=2 and m=4 as per the first example.
        """
        self.n = n
        self.m = m
    
    def case_generator(self):
        """
        Generate a puzzle instance (segments) ensuring no common integer point exists in all segments.
        """
        if self.m < 1:
            raise ValueError("m must be at least 1")
        if self.n < 1:
            raise ValueError("n must be at least 1")
        
        segments = []
        if self.m == 1:
            # Only one point, but must have no common point (impossible if n >=1). So this case is invalid.
            # But since m >=1 and n >=1, this can't happen as per problem constraints (guaranteed no common point)
            # For safety, handle edge case
            return {'n': 0, 'm': 1, 'segments': []}
        
        # Choose a split point to divide segments into left and right parts
        split_x = random.randint(1, self.m - 1)
        k = random.randint(0, self.n)  # number of segments on the left

        # Generate left segments (li <= ri <= split_x)
        for _ in range(k):
            li = random.randint(1, split_x)
            ri = random.randint(li, split_x)
            segments.append((li, ri))
        
        # Generate right segments (split_x+1 <= li <= ri <= m)
        for _ in range(self.n - k):
            li = random.randint(split_x + 1, self.m)
            ri = random.randint(li, self.m)
            segments.append((li, ri))
        
        # The case data
        return {
            'n': self.n,
            'm': self.m,
            'segments': segments
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        Convert the generated puzzle instance into a textual problem description with answer format instructions.
        """
        segments_str = '\n'.join([f"{li} {ri}" for li, ri in question_case['segments']])
        prompt = f"""Fteodorisnotaliar has drawn {question_case['n']} segments on integer points within [1, {question_case['m']}]. Sasha wants to determine the maximum number of questions he can ask such that even with the answers, he can't be sure Fteodorisnotaliar isn't lying. 

Problem Details:
- Number of segments (n): {question_case['n']}
- Maximum coordinate (m): {question_case['m']}
Segments (each as 'li ri'):
{segments_str}

Task:
Calculate the largest possible number of questions Sasha can ask (xi, count) where knowing all answers doesn't confirm Fteodorisnotaliar's truthfulness. 

Rules:
1. Each xi must be unique, 1 ≤ xi ≤ {question_case['m']}.
2. Fteodorisnotaliar's segments have no common integer point.
3. Sasha doesn't know n initially.

Output Requirement:
Your answer must be a single integer inside [answer]...[/answer] tags. Example: [answer]4[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

