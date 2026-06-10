import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_answer(n, k, links):
    x = [a - 1 for a in links]
    a = [0] * n
    for i in range(n):
        left = max(0, i - k)
        right = min(n - 1, i + k)
        visible = right - left + 1
        c = visible
        if x[i] != -1:
            if (i - x[i]) > 2 * k:
                c += a[x[i]]
            else:
                overlap_right = min(n - 1, x[i] + k)
                current_right = min(n - 1, i + k)
                additional = current_right - overlap_right
                c = a[x[i]] + additional
        a[i] = c
    return a


class BchatInstructionGenerator(BaseInstructionGenerator):
    """Bchat Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, **kwargs):
        """
        初始化Bchat指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        k = random.randint(0, n)
        links = []
        for i in range(1, n + 1):
            if i == 1:
                ai = 0
            else:
                choices = [0] + list(range(1, i))
                ai = random.choice(choices)
            links.append(ai)
        correct_output = compute_answer(n, k, links)
        return {
            'n': n,
            'k': k,
            'links': links,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        links = question_case['links']
        prompt = f"""You are analyzing your social network message history. Each message is numbered from 1 to {n} in chronological order. Each message may contain a link to an earlier message (strictly less than its own number) or no link. 

When you open a message x, you will see up to {k} previous messages, message x itself, and up to {k} next messages. If there are fewer than {k} messages in either direction, all available messages are shown. You repeatedly follow any links in the current message until there are no more links to follow. Each message is counted only once, regardless of how many times it is viewed.

Your task is to determine, for each starting message from 1 to {n}, the number of distinct messages read.

Input parameters:
- n = {n}
- k = {k}
- Links: {links} (each element a_i corresponds to the message linked by message i, where i ranges from 1 to {n}. A value of 0 indicates no link.)

Output a sequence of {n} integers separated by spaces, where the i-th integer corresponds to the result for starting at message i. Place your answer within [answer] and [/answer] tags. For example: [answer]1 2 3 4 5 6[/answer]"""

        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

