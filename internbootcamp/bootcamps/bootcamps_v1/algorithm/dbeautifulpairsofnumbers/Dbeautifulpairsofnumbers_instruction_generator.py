import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DbeautifulpairsofnumbersInstructionGenerator(BaseInstructionGenerator):
    """Dbeautifulpairsofnumbers Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, min_n=1, **kwargs):
        """
        初始化Dbeautifulpairsofnumbers指令生成器
        
        Args:
            max_n: 参数描述
            min_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
        self.min_n = min_n
        self.initialize_data()
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        k = random.randint(1, n)
        correct_answer = self.compute_answer(n, k)
        return {
            'n': n,
            'k': k,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        prompt = f"""你是一个算法竞赛选手，现在需要解决一个数学谜题。请仔细阅读以下问题描述，并输出你的答案。

问题描述:
给定一个正整数n和k，计算满足条件的“美丽序列”的数量。答案需要对1e9+7取模。

美丽序列的定义:
- 序列由k个整数对组成：(a1, b1), (a2, b2), ..., (ak, bk)。
- 满足以下两个条件：
  1. 所有整数对严格递增且互不重叠，即1 ≤ a1 ≤ b1 < a2 ≤ b2 < ... < ak ≤ bk ≤ n。
  2. 每个整数对的差（即bi - ai）互不相同。

输入要求:
- n的值为{n}，k的值为{k}。

输出要求:
- 输出满足条件的美丽序列的数量模1000000007的结果。

请将最终答案放在[answer]和[/answer]的标签之间。例如：[answer]42[/answer]。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def initialize_data(cls):
        if cls.initialized:
            return
        # Precompute factorial and inverse factorial arrays
        cls.fac = [1] * cls.maxn
        for i in range(1, cls.maxn):
            cls.fac[i] = cls.fac[i-1] * i % cls.mod

        cls.ifac = [1] * cls.maxn
        cls.ifac[cls.maxn - 1] = pow(cls.fac[cls.maxn - 1], cls.mod - 2, cls.mod)
        for i in range(cls.maxn - 2, -1, -1):
            cls.ifac[i] = cls.ifac[i + 1] * (i + 1) % cls.mod

        # Precompute s array
        cls.s = [0] * cls.maxn
        for i in range(1, cls.maxn):
            cls.s[i] = cls.s[i-1] + i

        # Initialize f array using dynamic programming
        cls.f = [[0] * cls.maxn for _ in range(cls.maxn)]
        for i in range(1, cls.maxn):
            cls.f[i][1] = 1

        for j in range(2, cls.maxn):
            if cls.s[j] >= cls.maxn:
                break
            if cls.s[j] < cls.maxn:
                cls.f[cls.s[j]][j] = cls.fac[j] % cls.mod
            for i in range(cls.s[j] + 1, cls.maxn):
                prev_i = i - j
                if prev_i >= 0:
                    term1 = cls.f[prev_i][j]
                    term2 = (cls.f[prev_i][j-1] * j) % cls.mod
                    cls.f[i][j] = (term1 + term2) % cls.mod

        cls.initialized = True

    @classmethod
    def compute_answer(cls, n, k):
        if k < 1 or k > n:
            return 0
        new_n = n - 1
        res = 0
        s_k_1 = cls.s[k-1]
        for i in range(s_k_1, new_n + 1):
            t = new_n - i - (k - 1)
            if t < 0:
                break
            comb = cls.C(k + t, t)
            if (i + k) >= cls.maxn or k >= cls.maxn:
                f_val = 0
            else:
                f_val = cls.f[i + k][k]
            res = (res + f_val * comb) % cls.mod
        return res

    @classmethod
    def C(cls, n, m):
        if m < 0 or m > n:
            return 0
        return cls.fac[n] * cls.ifac[m] % cls.mod * cls.ifac[n - m] % cls.mod
