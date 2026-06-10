import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def minimal_representation(s):
    n = len(s)
    if n == 0:
        return ''
    s += s
    i, j, k = 0, 1, 0
    while i < n and j < n and k < n:
        if s[i + k] == s[j + k]:
            k += 1
        else:
            if s[i + k] > s[j + k]:
                i += k + 1
            else:
                j += k + 1
            if i == j:
                j += 1
            k = 0
    min_pos = min(i, j)
    return s[min_pos:min_pos + n]


class EcyclicalquestInstructionGenerator(BaseInstructionGenerator):
    """Ecyclicalquest Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ecyclicalquest指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_s_length = params.get('max_s_length', 10)
        self.min_s_length = params.get('min_s_length', 5)
        self.max_queries = params.get('max_queries', 5)
        self.min_queries = params.get('min_queries', 1)
    
    def case_generator(self):
        def generate_random_string(length):
            return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=length))
        
        s_length = random.randint(self.min_s_length, self.max_s_length)
        s = generate_random_string(s_length)
        n = random.randint(self.min_queries, self.max_queries)
        queries = [generate_random_string(random.randint(1, s_length + 2)) for _ in range(n)]
        
        answers = []
        for xi in queries:
            xi_len = len(xi)
            if xi_len > len(s):
                answers.append(0)
                continue
            min_xi = minimal_representation(xi)
            count = 0
            substr_len = xi_len
            s_len = len(s)
            for i in range(s_len - substr_len + 1):
                substr = s[i:i + substr_len]
                if minimal_representation(substr) == min_xi:
                    count += 1
            answers.append(count)
        
        return {
            's': s,
            'n': n,
            'queries': queries,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case):
        s = question_case['s']
        n = question_case['n']
        queries = question_case['queries']
        problem = (
            "给定一个字符串 s 和若干查询字符串，每个查询要求计算 s 中连续子串与查询字符串循环同构的数量。"
            "两个字符串循环同构当且仅当其中一个可以通过旋转得到另一个（旋转指将前k个字符移到末尾）。\n\n"
            f"输入格式：\n第一行：{s}\n第二行：{n}\n接下来 {n} 行每行一个查询字符串：\n"
        )
        for xi in queries:
            problem += f"{xi}\n"
        problem += (
            "\n请按顺序输出每个查询的结果，每个结果占一行，置于[answer]和[/answer]之间。例如：\n"
            "[answer]\n3\n0\n5\n[/answer]\n"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

