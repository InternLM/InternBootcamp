import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import string
from collections import defaultdict
from collections import deque




class CdiversesubstringsInstructionGenerator(BaseInstructionGenerator):
    """Cdiversesubstrings Bootcamp指令生成器"""
    
    def __init__(self, min_length=4, max_length=100):
        """
        初始化Cdiversesubstrings指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = max(min_length, 1)
        self.max_length = max(max_length, self.min_length)
    
    def case_generator(self):
        # Generate string with controlled diversity
        length = random.randint(self.min_length, self.max_length)
        max_possible_d = min(26, length)
        target_d = random.randint(1, max_possible_d)
        
        # Ensure exactly target_d distinct characters
        base_chars = random.sample(string.ascii_lowercase, target_d)
        s_list = base_chars.copy()
        
        # Fill remaining length with random choices from base chars
        for _ in range(length - target_d):
            s_list.append(random.choice(base_chars))
        
        random.shuffle(s_list)
        s = ''.join(s_list)
        
        # Calculate actual d and t_list using optimized algorithm
        d = len(set(s))
        t_list = self.compute_t_list(s)
        
        return {
            's': s,
            'd': d,
            't_list': t_list
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        s = question_case['s']
        return f"""You are given a string consisting of lowercase Latin letters. The diversity of a string is defined as the number of distinct characters it contains. Your task is to calculate two things: 
1. The diversity value d(s) of the given string.
2. For each k from 1 to d(s), determine how many substrings have exactly k distinct characters.

Input string: {s}

Output Format:
- First line: d(s)
- Next d(s) lines: Each line contains the count of substrings with diversity exactly k (k from 1 to d(s))

Enclose your final answer within [answer] and [/answer] tags. For example:
[answer]
3
4
3
3
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def compute_t_list(self, s):
        n = len(s)
        s = [ord(c) - ord('a') for c in s]
        total_d = len(set(s))
        ans = [0] * (total_d + 1)  # ans[0] unused

        for k in range(1, total_d + 1):
            count = defaultdict(int)
            distinct = 0
            left = 0
            res = 0

            for right in range(n):
                c = s[right]
                if count[c] == 0:
                    distinct += 1
                count[c] += 1

                while distinct > k:
                    left_c = s[left]
                    count[left_c] -= 1
                    if count[left_c] == 0:
                        distinct -= 1
                    left += 1

                res += right - left + 1

            prev_res = 0
            if k > 1:
                prev_res = self.at_most_k(s, k-1)
            ans[k] = res - prev_res

        return [ans[k] for k in range(1, total_d+1)]

    def at_most_k(self, s, k):
        count = defaultdict(int)
        distinct = 0
        left = 0
        res = 0

        for right in range(len(s)):
            c = s[right]
            if count[c] == 0:
                distinct += 1
            count[c] += 1

            while distinct > k:
                left_c = s[left]
                count[left_c] -= 1
                if count[left_c] == 0:
                    distinct -= 1
                left += 1

            res += right - left + 1

        return res
