import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class BcountpairsInstructionGenerator(BaseInstructionGenerator):
    """Bcountpairs Bootcamp指令生成器"""
    
    def __init__(self, possible_p=None, n_min=2, n_max=10000, **kwargs):
        """
        初始化Bcountpairs指令生成器
        
        Args:
            possible_p: 参数描述
            n_min: 参数描述
            n_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        if possible_p is None:
            possible_p = [
                3, 5, 7, 11, 13, 17, 19, 23, 29,  # 小质数
                1009, 7919,  # 中等大小质数
                1000003, 1000000007  # 大质数示例
            ]
        self.possible_p = possible_p
        self.n_min = n_min
        self.n_max = n_max  # 默认上限调整为更接近题目范围
    
    def case_generator(self):
        p = random.choice(self.possible_p)
        k = random.randint(0, p - 1)
        max_n = min(p, self.n_max)
        n = random.randint(self.n_min, max_n)
        a = []
        seen = set()
        # 生成n个不同的a_i，避免大内存占用
        while len(a) < n:
            x = random.randint(0, p-1)
            if x not in seen:
                seen.add(x)
                a.append(x)
        # 计算正确答案
        rems = {}
        for x in a:
            x4_mod = pow(x, 4, p)
            kx_mod = (k * x) % p
            term = (x4_mod - kx_mod) % p
            rems[term] = rems.get(term, 0) + 1
        ans = sum(cnt * (cnt - 1) // 2 for cnt in rems.values())
        return {
            'n': n,
            'p': p,
            'k': k,
            'a': a,
            'ans': ans
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        p = question_case['p']
        k = question_case['k']
        a = question_case['a']
        a_str = ' '.join(map(str, a))
        prompt = f"""You are a programming expert. Solve the following problem.

Given a prime number p, a list of {n} distinct integers, and an integer k, your task is to find the number of pairs of indices (i, j) where 1 ≤ i < j ≤ n and the expression (a_i + a_j)(a_i² + a_j²) is congruent to k modulo p.

Input Format:
- The first line contains three integers n, p, k. Here, n is the number of integers (2 ≤ n ≤ 3e5), p is a prime number (2 ≤ p ≤ 1e9), and k is an integer (0 ≤ k ≤ p-1).
- The second line contains n distinct integers a_1, a_2, ..., a_n, each between 0 and p-1 inclusive.

Output Format:
Output a single integer, the number of valid pairs.

Example:
For input:
3 3 0
0 1 2
The correct output is 1, as only the pair (1, 3) satisfies the condition.

Now, solve the following input case:
Input:
{n} {p} {k}
{a_str}

Please provide your answer within the tags [answer] and [/answer]. Ensure your final answer is the last one within these tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

