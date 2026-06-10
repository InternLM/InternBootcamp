import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
import re
from collections import defaultdict




class CgamewithstringsInstructionGenerator(BaseInstructionGenerator):
    """Cgamewithstrings Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=50, min_m=1, max_m=20):
        """
        初始化Cgamewithstrings指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
    
    def case_generator(self):
        m = random.randint(self.min_m, self.max_m)
        n = random.randint(self.min_n, self.max_n)
        chars = string.ascii_letters
        strings = set()
        while len(strings) < n:
            s = ''.join(random.choice(chars) for _ in range(m))
            if s not in strings:
                strings.add(s)
        strings = list(strings)
        return {
            'n': n,
            'm': m,
            'strings': strings
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        strings = question_case['strings']
        input_lines = [str(n)] + strings
        input_str = '\n'.join(input_lines)
        prompt = f"""You are playing a game with your friend. The rules of the game are as follows:

Your friend creates {n} distinct strings of the same length and tells you all of them. He then randomly selects one string uniformly at random. Your task is to determine which string he selected by asking questions. Each question allows you to inquire about the character at a specific position in the string, which you haven't asked about before. You choose each position uniformly at random from the remaining positions. The process stops once the selected string is uniquely identified.

Your goal is to calculate the expected number of questions required to identify the chosen string.

Input format:
The first line contains an integer n (number of strings). The next n lines contain the distinct strings.

For example, the input may look like:
2
aab
aac

Your task is to compute the expected value, ensuring that the answer's absolute or relative error does not exceed 1e-9. Format your answer with at least 12 decimal places and enclose it within [answer] and [/answer] tags.

Input provided:
{input_str}

Please provide your answer within the specified tags."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_expected_value(strings):
        n = len(strings)
        if n == 0:
            return 0.0
        m = len(strings[0])
        if any(len(s) != m for s in strings):
            raise ValueError("All strings must have the same length")

        w = [0] * (1 << m)
        for i in range(n):
            for j in range(i):
                mask = 0
                for k in range(m):
                    if strings[i][k] == strings[j][k]:
                        mask |= 1 << k
                w[mask] |= (1 << i) | (1 << j)

        # Propagate the masks
        for mask in reversed(range(1 << m)):
            for k in range(m):
                if mask & (1 << k):
                    lower_mask = mask ^ (1 << k)
                    w[lower_mask] |= w[mask]

        cnt = [0] * (1 << m)
        for mask in range(1 << m):
            cnt[mask] = bin(w[mask]).count('1')

        dp = [0.0] * (1 << m)
        for mask in reversed(range(1 << m)):
            if cnt[mask] == 0:
                continue
            asked = bin(mask).count('1')
            remaining = m - asked
            if remaining == 0:
                dp[mask] = 0.0
                continue
            total = 0.0
            for k in range(m):
                if not (mask & (1 << k)):
                    next_mask = mask | (1 << k)
                    total += dp[next_mask] * cnt[next_mask]
            dp[mask] = 1 + total / (remaining * cnt[mask])
        return dp[0]
