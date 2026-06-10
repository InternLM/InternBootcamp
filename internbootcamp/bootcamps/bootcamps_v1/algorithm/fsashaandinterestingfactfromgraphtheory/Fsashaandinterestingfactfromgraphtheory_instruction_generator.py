import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class FsashaandinterestingfactfromgraphtheoryInstructionGenerator(BaseInstructionGenerator):
    """Fsashaandinterestingfactfromgraphtheory Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=10, m_min=1, m_max=10):
        """
        初始化Fsashaandinterestingfactfromgraphtheory指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_min: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 2)  # n至少为2
        self.n_max = n_max
        self.m_min = max(m_min, 1)  # m至少为1
        self.m_max = m_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        m = random.randint(self.m_min, self.m_max)
        a = random.randint(1, n)
        b = a
        while b == a:
            b = random.randint(1, n)
        return {
            'n': n,
            'm': m,
            'a': a,
            'b': b
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        a = question_case['a']
        b = question_case['b']
        return f"""You are solving a graph theory problem. Compute the number of beautiful trees modulo {MOD}.

Problem Details:
- Tree properties: {n} vertices, edges have weights from 1 to {m}
- Beautiful tree condition: Distance between vertex {a} and {b} must be exactly {m}
- Distance is the sum of edge weights on the path between them

Output Requirements:
1. Answer must be an integer
2. Place your final answer between [answer] and [/answer] tags

Example Valid Response:
The number of beautiful trees is [answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n, m):
        mod = MOD
        if n < 2 or m < 1:
            return 0

        # 动态计算代替预先生成大数组
        def comb(n, k):
            if n < 0 or k < 0 or k > n:
                return 0
            numerator = 1
            for i in range(n, n-k, -1):
                numerator = numerator * i % mod
            denominator = 1
            for i in range(1, k+1):
                denominator = denominator * i % mod
            return numerator * pow(denominator, mod-2, mod) % mod

        def perm(n, k):
            if n < 0 or k < 0 or k > n:
                return 0
            res = 1
            for i in range(n, n-k, -1):
                res = res * i % mod
            return res

        ans = 0
        for i in range(1, n):
            if i > m:
                break

            c = comb(m-1, i-1)
            a_val = perm(n-2, i-1)
            f_val = pow(m, max(n-1-i, 0), mod)
            term = c * a_val % mod
            term = term * f_val % mod

            if i < n-1:
                term = term * (i+1) % mod
                term = term * pow(n, n-i-2, mod) % mod

            ans = (ans + term) % mod

        return ans
