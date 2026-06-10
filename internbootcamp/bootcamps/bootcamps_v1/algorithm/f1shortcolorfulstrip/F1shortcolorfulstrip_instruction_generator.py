import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 998244353



# === 源文件中的全局函数 ===

def solve(n, c_list):
    C = [x - 1 for x in c_list]
    DP = [[1] * (n + 1) for _ in range(n + 1)]
    for le in range(1, n + 1):
        for i in range(n - le + 1):
            j = i + le
            k = min(range(i, j), key=lambda x: C[x])
            ans1 = 0
            for split in range(i, k + 1):
                ans1 = (ans1 + DP[i][split] * DP[split][k]) % MOD
            ans2 = 0
            for split in range(k + 1, j + 1):
                ans2 = (ans2 + DP[k + 1][split] * DP[split][j]) % MOD
            DP[i][j] = (ans1 * ans2) % MOD
    return DP[0][n] % MOD


class F1shortcolorfulstripInstructionGenerator(BaseInstructionGenerator):
    """F1shortcolorfulstrip Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=7):
        """
        初始化F1shortcolorfulstrip指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        c = list(range(1, n + 1))
        random.shuffle(c)
        correct_answer = solve(n, c)
        return {
            'n': n,
            'm': n,
            'c': c,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        c = question_case['c']
        c_str = ' '.join(map(str, c))
        prompt = f"""You are tasked with solving a programming puzzle. Please find the number of valid ways Alice could have painted a strip of paper according to the rules described, and provide the answer modulo 998244353.

Problem Description:
- The strip is initially painted with color 0.
- Alice repaints segments in n steps, each time using a new color from 1 to n.
- Each segment repainted must be a single continuous block of the same color before repainting.
- The final color of each 1 cm segment [i-1, i] is given as a permutation of 1 through n.

Input:
- The first line contains two integers n and m (n = m = {n} in this case).
- The second line contains the colors of each segment as a permutation: {c_str}

Output:
- A single integer representing the number of valid ways modulo 998244353.

Ensure your final answer is enclosed within [answer] and [/answer] tags. Example: [answer]123[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

