import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import json
import random




class EnumbertransformationiiInstructionGenerator(BaseInstructionGenerator):
    """Enumbertransformationii Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=100, xi_min=2, xi_max=10**9, a_min=100, a_max=10**9, diff_min=1, diff_max=10**6):
        """
        初始化Enumbertransformationii指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            xi_min: 参数描述
            xi_max: 参数描述
            a_min: 参数描述
            a_max: 参数描述
            diff_min: 参数描述
            diff_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n_min = n_min
        self.n_max = n_max
        self.xi_min = xi_min
        self.xi_max = xi_max
        self.a_min = a_min
        self.a_max = a_max
        self.diff_min = diff_min
        self.diff_max = diff_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        xi = [random.randint(self.xi_min, self.xi_max) for _ in range(n)]
        xi = list(set(xi))  # 去重
        xi.sort(reverse=True)
        b = random.randint(0, self.a_max - self.diff_min)
        diff = random.randint(self.diff_min, self.diff_max)
        a = b + diff
        case = {
            'n': n,
            'xi': xi,
            'a': a,
            'b': b
        }
        return case
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        xi = question_case['xi']
        a = question_case['a']
        b = question_case['b']
        prompt = f"你有一个序列的正整数x1, x2, ..., xn，以及两个非负整数a和b。你的任务是将a转换为b，使用尽可能少的步骤。允许的操作有两种：1. 减去1；2. 减去a mod xi中的一个xi，其中xi是序列中的一个数。例如，如果a=30，xi=[3,4,5]，那么a mod 3是0，mod4是2，mod5是0。那么，可以选择减去0（这其实是无效操作，因为a不变），或者减去2。所以，操作后a变为28。请给定以下参数，求最小的操作次数：\n\nn = {n}\nxi = {xi}\na = {a}\nb = {b}\n\n请将你的答案放在[answer]标签中，例如：[answer]6[/answer]。"
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_min_steps(a, b, xi):
        if a == b:
            return 0
        xi = sorted(list(set(xi)), reverse=True)
        count = 0
        be = 0
        while a > b and be < len(xi):
            max_step = 0
            new_be = be
            for i in range(be, len(xi)):
                mod = a % xi[i]
                if mod == 0:
                    continue
                if a - mod >= b:
                    if mod > max_step:
                        max_step = mod
                        new_be = i + 1
                else:
                    new_be = i + 1
                    break
            if max_step > 0:
                a -= max_step
                count += 1
                be = new_be
            else:
                a -= 1
                count += 1
        count += (a - b)
        return count
