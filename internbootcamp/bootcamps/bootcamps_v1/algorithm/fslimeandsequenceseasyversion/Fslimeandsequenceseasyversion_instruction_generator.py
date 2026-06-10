import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

MOD = 998244353


class FslimeandsequenceseasyversionInstructionGenerator(BaseInstructionGenerator):
    """Fslimeandsequenceseasyversion Bootcamp指令生成器"""
    
    def __init__(self, max_n=100):
        """
        初始化Fslimeandsequenceseasyversion指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        限制默认max_n以保证生成效率，用户可自行设置更大值
        """
        self.max_n = min(max_n, 5000)  # 强制不超过题目要求的5000上限
    
    def case_generator(self):
        import random
        n = random.randint(1, self.max_n)
        expected = self.compute_answer(n)
        return {'n': n, 'expected': expected}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        return f"""Given n = {n}, compute the sum of occurrences for each k (1-{n}) in all valid sequences. Enclose your answer in [answer][/answer] tags.

Sample format:
n=2 → [answer]3 1[/answer]
n=3 → [answer]10 7 1[/answer]

Rules:
1. For any k>1 in sequence, must have earlier k-1
2. Output n space-separated values mod 998244353
3. Numbers must be in order from k=1 to k={n}

Your answer for n={n}:""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_answer(n):
        mod = MOD
        if n == 0:
            return []

        # 预计算阶乘和逆阶乘
        fac = [1]*(n+1)
        for i in range(1, n+1):
            fac[i] = fac[i-1] * i % mod

        inv_fac = [1]*(n+1)
        inv_fac[n] = pow(fac[n], mod-2, mod)
        for i in range(n-1, -1, -1):
            inv_fac[i] = inv_fac[i+1] * (i+1) % mod

        # 使用滚动数组优化空间
        ans = [0]*(n+2)
        prev = [0]*(n+2)
        prev[0] = 1

        for i in range(1, n+1):
            curr = [0]*(n+2)
            for j in range(1, i+1):
                term1 = prev[j] * j % mod
                term2 = prev[j-1] * (i-j+1) % mod
                curr[j] = (term1 + term2) % mod

            # 实时累加结果，避免存储全表
            for j in range(1, i+1):
                ans[j] = (ans[j] + curr[j] * inv_fac[i]) % mod

            prev = curr  # 滚动更新

        # 最终调整
        return [ans[j] * fac[n] % mod for j in range(1, n+1)]
