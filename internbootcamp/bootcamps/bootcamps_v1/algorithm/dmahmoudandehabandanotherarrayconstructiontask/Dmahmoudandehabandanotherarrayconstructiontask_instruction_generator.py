import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DmahmoudandehabandanotherarrayconstructiontaskInstructionGenerator(BaseInstructionGenerator):
    """Dmahmoudandehabandanotherarrayconstructiontask Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_ai=100):
        """
        初始化Dmahmoudandehabandanotherarrayconstructiontask指令生成器
        
        Args:
            max_n: 参数描述
            max_ai: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_ai = max_ai
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        a = [random.randint(2, self.max_ai) for _ in range(n)]
        expected_b = self.generate_b(a)
        return {
            'n': n,
            'a': a,
            'expected_b': expected_b
        }
    
    @staticmethod
    def prompt_func(question_case):
        a_str = ' '.join(map(str, question_case['a']))
        return (
            f"You are given an array a of {question_case['n']} integers. Your task is to construct the lexicographically smallest array b that meets the following conditions:\n\n"
            "1. The array b is lexicographically greater than or equal to a.\n"
            "2. Each element in b is at least 2.\n"
            "3. All elements in b are pairwise coprime (their GCD must be 1).\n\n"
            f"Input array a: {a_str}\n\n"
            "Output the space-separated elements of array b. Enclose your answer within [answer] and [/answer] tags."
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_b(a):
        MAX_NUM = 2000000
        prime_str = ('2 3 5 7 11 13 17 19 23 29 '
                     '31 37 41 43 47 53 59 61 67 71 '
                     '73 79 83 89 97 101 103 107 109 113 '
                     '127 131 137 139 149 151 157 163 167 173 '
                     '179 181 191 193 197 199 211 223 227 229 '
                     '233 239 241 251 257 263 269 271 277 281 '
                     '283 293 307 311 313 317')
        prime_list = [int(p) for p in prime_str.split()]
        used = [False] * (MAX_NUM + 1)
        n = len(a)
        b = []

        def record(x):
            t = []
            tmp_x = x
            for p in prime_list:
                if tmp_x % p == 0:
                    while tmp_x % p == 0:
                        tmp_x = tmp_x // p
                    t.append(p)
                    if tmp_x == 1:
                        break
            if tmp_x != 1:
                t.append(tmp_x)
            for ti in t:
                if ti > MAX_NUM:
                    continue
                for i in range(ti, MAX_NUM + 1, ti):
                    used[i] = True

        for ai in a:
            if ai <= MAX_NUM and not used[ai]:
                b.append(ai)
                record(ai)
            else:
                temp = ai + 1
                while temp <= MAX_NUM and used[temp]:
                    temp += 1
                if temp > MAX_NUM:
                    temp = ai + 1
                b.append(temp)
                record(temp)
                break  # Break after first replacement

        temp = 2
        while len(b) < len(a):
            while temp <= MAX_NUM and used[temp]:
                temp += 1
            if temp > MAX_NUM:
                break
            b.append(temp)
            record(temp)
            temp += 1

        return b
