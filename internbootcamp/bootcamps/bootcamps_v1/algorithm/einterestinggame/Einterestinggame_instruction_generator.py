import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from functools import reduce
from operator import xor
import re
import random




class EinterestinggameInstructionGenerator(BaseInstructionGenerator):
    """Einterestinggame Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=100000):
        """
        初始化Einterestinggame指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.win_dict = {}
        self.precompute()
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        return {'n': n, 'correct_answer': self.win_dict.get(n, -1)}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""Two friends Serozha and Gena play a stone splitting game. Initially there is 1 pile of {n} stones. On each turn, a player splits a pile into ≥2 strictly decreasing piles with consecutive differences of 1. The player who cannot move loses. Serozha goes first.

If Serozha can win with optimal play, find the minimal k (number of piles he splits into on his first move). Otherwise, output -1. 

Format your answer as [answer]k[/answer] where k is -1 or an integer ≥2.

Examples:
Input: 3 → Output: [answer]2[/answer]
Input: 6 → Output: [answer]-1[/answer]
Input: 100 → Output: [answer]8[/answer]
Your task: {n}""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def split(self, stone, k):
        total = k * (k - 1) // 2
        numerator = stone + total
        if numerator % k != 0:
            return []
        a = numerator // k
        if a < k:
            return []
        piles = [a - i for i in range(k)]
        if sum(piles) != stone:
            return []
        return piles

    def mex(self, s):
        i = 0
        while i in s:
            i += 1
        return i

    def precompute(self):
        self.win_dict = {1: -1, 2: -1}
        known = {1: 0, 2: 0}
        for stone in range(3, self.max_n + 1):
            mex_set = set()
            win_k = -1
            max_k = int((2 * stone) ** 0.5) + 1
            for k in range(2, max_k + 1):
                piles = self.split(stone, k)
                if not piles:
                    continue
                try:
                    xor_val = reduce(xor, (known[p] for p in piles))
                except KeyError:
                    continue
                mex_set.add(xor_val)
                if xor_val == 0 and win_k == -1:
                    win_k = k
            mex_val = self.mex(mex_set)
            known[stone] = mex_val
            self.win_dict[stone] = win_k
