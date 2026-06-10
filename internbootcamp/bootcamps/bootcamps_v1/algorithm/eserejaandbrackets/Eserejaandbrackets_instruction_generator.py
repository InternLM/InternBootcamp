import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_query(s, l, r):
    if l > r:
        return (0, 0, 0)
    if l == r:
        if s[l] == '(':
            return (0, 1, 0)
        else:
            return (0, 0, 1)
    mid = (l + r) // 2
    left_c, left_f, left_s = compute_query(s, l, mid)
    right_c, right_f, right_s = compute_query(s, mid + 1, r)
    extra = min(left_f, right_s)
    c = left_c + right_c + extra
    f = left_f + right_f - extra
    s_total = left_s + right_s - extra
    return (c, f, s_total)


class EserejaandbracketsInstructionGenerator(BaseInstructionGenerator):
    """Eserejaandbrackets Bootcamp指令生成器"""
    
    def __init__(self, n=10, m=3):
        """
        初始化Eserejaandbrackets指令生成器
        
        Args:
            n: 参数描述
            m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        初始化括号查询训练场，设置默认的字符串长度n和查询数量m。
        """
        self.n = n
        self.m = m
    
    def case_generator(self):
        """
        生成一个随机的括号字符串和相应的查询区间。
        """
        s = ''.join(random.choice(['(', ')']) for _ in range(self.n))
        queries = []
        for _ in range(self.m):
            li = random.randint(1, self.n)
            ri = random.randint(li, self.n)
            queries.append([li, ri])
        return {
            "s": s,
            "queries": queries
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        queries = question_case['queries']
        m = len(queries)
        input_lines = [s, str(m)]
        input_lines.extend(f"{l} {r}" for l, r in queries)
        input_str = '\n'.join(input_lines)
        prompt = f"""Sereja有一个由括号组成的字符串s，其长度为{len(s)}。他需要处理{m}个查询，每个查询要求找出特定区间内的最长有效括号子序列的长度。有效括号子序列是指可以通过插入数字和运算符形成合法算术表达式的括号序列。

例如，输入：
())(())(())(
7
1 1
2 3
...（其余查询）

对应的输出为每个查询的答案，每个答案占一行。

请解决以下问题：
输入：
{input_str}

请按照顺序输出每个查询的结果，每个结果占一行，并将所有答案放在[answer]和[/answer]标签之间。例如：
[answer]
0
0
2
...
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

