import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, digits_str):
    if n == 0:
        return 0
    d = [int(c) for c in digits_str]
    if n == 1:
        return 1
    
    # Initialize comparison matrix
    comp = [[0]*(n+1) for _ in range(n)]
    
    for l in range(1, n):
        equal_count = 0
        for i in range(n - l):
            j = i + l
            if d[i] == d[j]:
                equal_count += 1
                if equal_count >= l:
                    equal_count = l - 1
            else:
                if d[i] < d[j]:
                    # Mark all positions in the equal prefix
                    start = i - equal_count
                    end = i + 1
                    for k in range(start, end):
                        if k >= 0 and j - equal_count + (k - start) < n:
                            comp[k][j - equal_count + (k - start) + 1] = 1
                equal_count = 0
    
    # Dynamic programming table
    dp = [[0]*(n+1) for _ in range(n+1)]
    for j in range(1, n+1):
        dp[j][j] = 1
    
    # Fill DP table
    for i in range(1, n):
        if d[i] == 0:
            continue
        prefix_sum = 0
        for l in range(1, n - i + 1):
            prefix_sum = (prefix_sum + dp[i][l-1]) % MOD
            if l <= i:
                compare_pos = i - l
                if compare_pos >= 0 and comp[compare_pos][i]:
                    dp[i+l][l] = (prefix_sum + dp[i][l]) % MOD
                else:
                    dp[i+l][l] = prefix_sum
            else:
                dp[i+l][l] = prefix_sum
    
    # Calculate final answer
    total = 0
    for l in range(1, n+1):
        total = (total + dp[n][l]) % MOD
    return total


class DnewyearandancientprophecyInstructionGenerator(BaseInstructionGenerator):
    """Dnewyearandancientprophecy Bootcamp指令生成器"""
    
    def __init__(self, min_length=1, max_length=20):
        """
        初始化Dnewyearandancientprophecy指令生成器
        
        Args:
            min_length: 参数描述
            max_length: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_length = min_length
        self.max_length = max_length
    
    def case_generator(self):
        # Ensure reasonable case generation for computation efficiency
        n = random.randint(self.min_length, min(self.max_length, 100))
        first_digit = random.randint(1, 9)
        rest = ''.join(str(random.randint(0, 9)) for _ in range(n-1))
        digits = str(first_digit) + rest
        
        return {
            'n': n,
            'digits': digits,
            'correct_answer': compute_answer(n, digits)
        }
    
    @staticmethod
    def prompt_func(question_case):
        return f"""Given a digit sequence of length {question_case['n']}: {question_case['digits']}
        
Task requirements:
1. Split the sequence into strictly increasing integers
2. No leading zeros in any number
3. Calculate the number of valid splits modulo 10^9+7

Examples:
Input: 6\n123434 → Output:8
Input:8\n20152016 → Output:4

Format your final answer within [answer] tags like: [answer]123[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

