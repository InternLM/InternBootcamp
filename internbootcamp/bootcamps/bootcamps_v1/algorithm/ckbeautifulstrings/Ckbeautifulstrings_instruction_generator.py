import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import sys
import re
import random

# === 源文件中的全局函数 ===

def getnext(index, fre, k, s, flag):
    if sum(fre) > len(s) - index:
        return "ERROR"
    if index == len(s):
        return ""
    cur = ord(s[index]) - 97 if index < len(s) else 0
    if not flag:
        spare = len(s) - index - sum(fre)
        nexts = ""
        if spare % k == 0:
            nexts += 'a' * (spare // k * k)
        for j in range(26):
            if fre[j] > 0:
                nexts += chr(j + 97) * fre[j]
        return nexts
    nexts = "ERROR"
    for j in range(cur, 26):
        new_flag = flag
        if j > cur:
            new_flag = False
        original_j = fre[j]
        fre[j] -= 1
        if fre[j] < 0:
            fre[j] += k
        temp = getnext(index + 1, fre, k, s, new_flag)
        if temp != "ERROR":
            nexts = chr(j + 97) + temp
            fre[j] = original_j
            return nexts
        fre[j] = original_j
    return nexts

def solve(n, k, s):
    if n % k != 0:
        return "-1"
    fre = [0] * 26
    ans = getnext(0, fre, k, s, True)
    return ans if ans != "ERROR" else "-1"


class CkbeautifulstringsInstructionGenerator(BaseInstructionGenerator):
    """Ckbeautifulstrings Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_k=20):
        """
        初始化Ckbeautifulstrings指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_k = max_k
    
    def case_generator(self):
        while True:
            if random.choice([True, False]):
                # Generate unsolvable case
                while True:
                    n = random.randint(1, self.max_n)
                    k = random.randint(1, self.max_n)
                    if n % k != 0:
                        break
                s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=n))
                return {'n': n, 'k': k, 's': s}
            else:
                # Generate solvable case
                k = random.randint(1, self.max_k)
                max_multiplier = self.max_n // k
                if max_multiplier < 1:
                    continue
                multiplier = random.randint(1, max_multiplier)
                n = k * multiplier
                s = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=n))
                solution = solve(n, k, s)
                if solution != "-1":
                    return {'n': n, 'k': k, 's': s}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        s = question_case['s']
        prompt = f"""You are given a string s of length {n} consisting of lowercase English letters and an integer k={k}. A string is called beautiful if the count of each character is divisible by k. Your task is to find the lexicographically smallest beautiful string of length {n} that is greater than or equal to s. If no such string exists, output -1.

Input:
- The string s is "{s}"
- The values are n={n}, k={k}

Please provide your answer enclosed within [answer] and [/answer]. For example: [answer]your_answer[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

