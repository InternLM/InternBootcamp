import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from math import isclose




class ElruInstructionGenerator(BaseInstructionGenerator):
    """Elru Bootcamp指令生成器"""
    
    def __init__(self, n=None, k=None):
        """
        初始化Elru指令生成器
        
        Args:
            n: 参数描述
            k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        if n is not None:
            if not (1 <= n <= 20):
                raise ValueError("n must be between 1 and 20")
        if k is not None:
            if k < 1:
                raise ValueError("k must be at least 1")
            if n is not None and k > n:
                raise ValueError(f"k ({k}) cannot exceed n ({n})")
        self.n = n
        self.k = k
    
    def case_generator(self):
        if self.n is None:
            n = random.randint(1, 20)
        else:
            n = self.n
        if self.k is None:
            k = random.randint(1, n)
        else:
            k = self.k
        k = min(k, n)
        
        integers = self._generate_integers(n)
        p = [round(x / 100.0, 2) for x in integers]  # Ensure exactly two decimal places
        
        # Validate sum of probabilities
        total = round(sum(p), 2)
        if total != 1.0:
            adjust = round(1.0 - total + p[-1], 2)
            p[-1] = adjust
        
        return {
            'n': n,
            'k': k,
            'p': p
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        p = question_case['p']
        p_str = ' '.join(f"{pi:.2f}" for pi in p)
        prompt = f"""You are analyzing an LRU cache with {n} videos (cache size {k}). Each video has access probabilities: {p_str}. Compute each video's steady-state cache presence probability. Format your answer as space-separated numbers with 12+ decimals within [answer][/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _generate_integers(n):
        sum_total = 100
        if n == 1:
            return [sum_total]
        dividers = sorted(random.sample(range(1, sum_total + n), n - 1))
        dividers = [0] + dividers + [sum_total + n]
        parts = []
        for i in range(1, len(dividers)):
            parts.append(dividers[i] - dividers[i-1] - 1)
        return parts

    @staticmethod
    def calculate_probabilities(n, k, p):
        max_mask = 1 << n
        dp = [0.0] * max_mask
        dp[0] = 1.0
        a = [0.0] * n

        for mask in range(max_mask):
            cnt = bin(mask).count('1')
            sum_p = sum(p[i] for i in range(n) if (mask & (1 << i)))

            if cnt == k or abs(sum_p - 1.0) < 1e-9:
                for i in range(n):
                    if mask & (1 << i):
                        a[i] += dp[mask]
                continue

            available = 1.0 - sum_p
            if available < 1e-9:
                continue
            for i in range(n):
                if not (mask & (1 << i)):
                    prob = p[i] / available
                    new_mask = mask | (1 << i)
                    dp[new_mask] += dp[mask] * prob
        return a
