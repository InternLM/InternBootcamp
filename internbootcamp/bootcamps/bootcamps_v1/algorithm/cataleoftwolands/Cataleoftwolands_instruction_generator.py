import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
import random
import re




class CataleoftwolandsInstructionGenerator(BaseInstructionGenerator):
    """Cataleoftwolands Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, min_n=2, min_val=0, max_val=20, allow_negative=True):
        """
        初始化Cataleoftwolands指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
            min_val: 参数描述
            max_val: 参数描述
            allow_negative: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.min_n = min_n
        self.min_val = min_val
        self.max_val = max_val
        self.allow_negative = allow_negative
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        existing = set()
        a = []
        while len(a) < n:
            num = random.randint(self.min_val, self.max_val)
            if self.allow_negative and random.choice([True, False]):
                num *= -1
            if num not in existing:
                a.append(num)
                existing.add(num)
        return {'n': n, 'a': a}
    
    @staticmethod
    def prompt_func(question_case):
        a_list = question_case['a']
        a_str = ' '.join(map(str, a_list))
        return f"""You are tasked with solving a historical mathematics problem about Vectorland and Arrayland. 

**Problem Statement:**
Two integers x and y form a valid pair if the Arrayland interval [min(|x|, |y|), max(|x|, |y|)] is fully contained within the Vectorland interval [min(|x−y|, |x+y|), max(|x−y|, |x+y|)]. 

**Input Format:**
- First line: Integer n (2 ≤ n ≤ 2×10^5)
- Second line: n distinct integers (space-separated)

**Sample Input 1:**
3
2 5 -3

**Sample Output 1:**
2

**Your Input:**
{question_case['n']}
{a_str}

Calculate the answer and put ONLY THE FINAL INTEGER within [answer] tags like: [answer]5[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

