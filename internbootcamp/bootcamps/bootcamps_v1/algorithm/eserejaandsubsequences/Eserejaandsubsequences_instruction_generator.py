import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EserejaandsubsequencesInstructionGenerator(BaseInstructionGenerator):
    """Eserejaandsubsequences Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=5, min_val=1, max_val=10, seed=None):
        """
        初始化Eserejaandsubsequences指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_val: 参数描述
            max_val: 参数描述
            seed: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_val = min_val
        self.max_val = max_val
        self.seed = seed
        if seed is not None:
            random.seed(seed)
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        a = [random.randint(self.min_val, self.max_val) for _ in range(n)]
        answer = self.compute_answer(a)
        return {
            'n': n,
            'a': a,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        a = question_case['a']
        a_str = ' '.join(map(str, a))
        problem_text = f"""Sereja有一个由n个正整数组成的序列a。你需要解决以下问题：

问题描述：
找出所有不同的非空非递减子序列y。然后，对于每个y，计算所有可能的序列x的数量，其中x的长度与y相同，并且每个对应的元素x_i ≤ y_i。所有x的数量的总和模1000000007即为答案。

子序列定义：
- 子序列的元素保持原序列中的相对顺序，但可以删除某些元素。
- 非递减：子序列中的每个元素不小于前一个元素。
- 不同的子序列由它们的元素序列决定，即相同的元素序列被视为同一个子序列，即使它们来自原序列的不同位置。

输入格式：
- 第一行包含整数n（1 ≤ n ≤ 1e5）。
- 第二行包含n个正整数a_1, a_2, ..., a_n（1 ≤ a_i ≤ 1e6）。

你的任务：
给定n和序列a，计算最终的答案并以模1e9+7输出。

输入样例：
{n}
{a_str}

请按照上述输入样例的格式，计算出正确的答案，并将最终答案用[answer]和[/answer]标签包裹。例如：[answer]42[/answer]。"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(a):
        mod = 10**9 + 7
        if not a:
            return 0
        max_val = max(a)
        tree = [0] * (max_val + 2)  # Extra space to avoid index issues
        last = {}
        total = 0

        for x in a:
            # Query sum of all elements <= x
            sum_prev = 0
            idx = x
            while idx > 0:
                sum_prev = (sum_prev + tree[idx]) % mod
                idx -= idx & -idx

            # Calculate new contribution
            new_contrib = (sum_prev * x + x) % mod
            delta = (new_contrib - last.get(x, 0)) % mod

            # Update Fenwick tree
            idx = x
            while idx <= max_val:
                tree[idx] = (tree[idx] + delta) % mod
                idx += idx & -idx

            # Update last and total
            last[x] = new_contrib
            total = (total + delta) % mod

        return total
