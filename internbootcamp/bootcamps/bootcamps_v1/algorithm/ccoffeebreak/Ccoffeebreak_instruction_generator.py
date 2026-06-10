import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from heapq import heappush
from heapq import heappop
import re
from collections import defaultdict




class CcoffeebreakInstructionGenerator(BaseInstructionGenerator):
    """Ccoffeebreak Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=100):
        """
        初始化Ccoffeebreak指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(n, self.max_m)
        a = random.sample(range(1, m + 1), n)
        d = random.randint(1, m)
        return {
            'n': n,
            'm': m,
            'd': d,
            'a': a
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        d = question_case['d']
        a_list = question_case['a']
        a_str = ' '.join(map(str, a_list))
        prompt = f"""Monocarp wants to schedule his coffee breaks during his working day, which lasts for {m} minutes. He has specified {n} distinct minutes during which he would like to have coffee. However, his boss requires that any two consecutive coffee breaks on the same day must be at least {d} minutes apart. Your task is to determine the minimum number of days required and assign each coffee break to a specific day, ensuring that the breaks on the same day are spaced appropriately. Days are numbered starting from 1.

The coffee break minutes are: {a_str}

Your answer must be formatted as follows:

[answer]
<minimum number of days>
<space-separated day assignments in the order of the input>
[/answer]

For example, if the minimum days is 3 and the assignments are 1, 2, 1, the answer should be:

[answer]
3
1 2 1
[/answer]

Please ensure the answer is enclosed within [answer] and [/answer] tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

