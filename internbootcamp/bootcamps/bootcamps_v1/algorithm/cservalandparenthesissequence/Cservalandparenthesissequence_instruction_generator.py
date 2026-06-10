import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CservalandparenthesissequenceInstructionGenerator(BaseInstructionGenerator):
    """Cservalandparenthesissequence Bootcamp指令生成器"""
    
    def __init__(self, min_length=2, max_length=20, replace_prob=0.3):
        """
        初始化Cservalandparenthesissequence指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
            replace_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        min_length = max(2, min_length)
        max_length = max(min_length, max_length)
        self.min_length = (min_length + 1) // 2 * 2  # 强制偶数
        self.max_length = (max_length // 2) * 2
        self.replace_prob = replace_prob
    
    def case_generator(self):
        # 随机生成长度（保证偶数）
        n = random.randint(self.min_length // 2, self.max_length // 2) * 2
        # 生成随机包含 (、)、? 的字符串
        s = []
        # 首字符允许生成 ) 来制造无法解决的情况
        first_char = random.choice(['(', ')', '?'])
        s.append(first_char)
        # 剩余字符随机生成
        for _ in range(n-1):
            s.append(random.choice(['(', ')', '?']))
        # 随机替换部分非?字符为?
        for i in range(n):
            if s[i] != '?' and random.random() < self.replace_prob:
                s[i] = '?'
        return {'n': n, 's': ''.join(s)}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        s = question_case['s']
        prompt = (
            "Replace '?' in the string to form a valid parenthesis sequence where all strict prefixes are invalid.\n"
            f"Input length: {n}\n"
            f"Input string: {s}\n\n"
            "Output the solution string or ':('. Enclose your answer within [answer]...[/answer]."
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_parenthesis(s):
        n = len(s)
        if n % 2 != 0:
            return ':('
        h = n // 2
        no = s.count('(')
        nc = s.count(')')
        nq = n - no - nc
        if no > h or nc > h or s[0] == ')':
            return ':('
        res = list(s)
        open_needed = h - no
        close_needed = h - nc
        if open_needed < 0 or close_needed < 0:
            return ':('
        # 遍历填充?
        cur_balance = 0
        for i in range(n):
            if res[i] == '(':
                cur_balance += 1
            elif res[i] == ')':
                cur_balance -= 1
                if cur_balance < 1 and i < n-1:
                    return ':('
            elif res[i] == '?':
                # 优先填 ( 的条件
                if open_needed > 0:
                    res[i] = '('
                    cur_balance += 1
                    open_needed -= 1
                else:
                    res[i] = ')'
                    cur_balance -= 1
                    close_needed -= 1
                # 检查中间非法情况
                if cur_balance < 0 or (cur_balance < 1 and i < n-1):
                    return ':('
        # 最终平衡检查
        return ''.join(res) if cur_balance == 0 else ':('

    @staticmethod
    def is_valid_parenthesis(s):
        balance = 0
        for c in s:
            balance += 1 if c == '(' else -1
            if balance < 0:
                return False
        return balance == 0
