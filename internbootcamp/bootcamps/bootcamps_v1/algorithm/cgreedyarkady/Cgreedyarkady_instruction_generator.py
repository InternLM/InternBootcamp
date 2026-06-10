import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CgreedyarkadyInstructionGenerator(BaseInstructionGenerator):
    """Cgreedyarkady Bootcamp指令生成器"""
    
    def __init__(self, max_k=20, max_D=20, M_range=100, **params):
        """
        初始化Cgreedyarkady指令生成器
        
        Args:
            max_k: 参数描述
            max_D: 参数描述
            M_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_k = max_k
        self.max_D = max_D
        self.M_range = M_range
        super().__init__(**params)
    
    def case_generator(self):
        k = random.randint(2, self.max_k)
        D = random.randint(1, self.max_D)
        n_min = max(2, k, D)
        denominator = k * D
        M_min = max(1, (n_min + denominator - 1) // denominator)
        M = random.randint(M_min, M_min + self.M_range)
        max_n = M * k * D
        lower = max(n_min, M)
        if lower > max_n:
            raise ValueError("Invalid parameters: lower exceeds max_n")
        n = random.randint(lower, max_n)
        assert 2 <= k <= n and 1 <= M <= n and 1 <= D <= min(n, 1000) and M * D * k >= n
        return {'n': n, 'k': k, 'M': M, 'D': D}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        M = question_case['M']
        D = question_case['D']
        return f"""Arkady和其他{k-1}个人要分配{n}颗糖果。每个糖果必须分给其中一人或丢弃。他们按照如下方式分配糖果：
Arkady选择一个整数x，然后按轮次分配：第一轮分x颗给自己，x颗给第二人，依此类推，直到第{k}人。然后第二轮继续每人分配x颗，直到剩余的糖果不足以分配给整个轮次的所有人，此时剩下的糖果将被丢弃。选择的x必须满足以下条件：
1. x不能超过给定的最大值M（即x ≤ {M}）。
2. 任何一个人（包括Arkady）被分配糖果的次数不能超过D次（即最多D次）。
在满足这些条件的情况下，Arkady希望自己获得的糖果总数尽可能多。请计算他能得到的最大糖果数。
输入参数：
n（糖果总数） = {n}
k（人数） = {k}
M（x的最大允许值） = {M}
D（每人最多分配次数） = {D}
请将最终答案放置在[answer]和[/answer]标签之间。例如，如果正确结果是5，应写成[answer]5[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

