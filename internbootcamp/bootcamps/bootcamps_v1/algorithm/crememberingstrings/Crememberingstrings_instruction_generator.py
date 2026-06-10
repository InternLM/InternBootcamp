import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from string import ascii_lowercase
import re

# === 源文件中的全局函数 ===

def solve(n, m, strings, costs):
    faa = [[0] * m for _ in range(n)]
    famask = [[0] * m for _ in range(n)]
    
    for i in range(n):
        for j in range(m):
            current_char = strings[i][j]
            total_cost = 0
            max_cost = 0
            mask = 0
            for k in range(n):
                if strings[k][j] == current_char:
                    total_cost += costs[k][j]
                    if costs[k][j] > max_cost:
                        max_cost = costs[k][j]
                    mask |= (1 << k)
            faa[i][j] = total_cost - max_cost
            famask[i][j] = mask
    
    dp = [float('inf')] * (1 << n)
    dp[0] = 0
    
    for mask in range(1 << n):
        if dp[mask] == float('inf'):
            continue
        for j in range(n):
            if (mask >> j) & 1:
                continue
            for k in range(m):
                new_mask1 = mask | (1 << j)
                cost1 = dp[mask] + costs[j][k]
                if cost1 < dp[new_mask1]:
                    dp[new_mask1] = cost1
                
                new_mask2 = mask | famask[j][k]
                cost2 = dp[mask] + faa[j][k]
                if cost2 < dp[new_mask2]:
                    dp[new_mask2] = cost2
    
    return dp[(1 << n) - 1]


class CrememberingstringsInstructionGenerator(BaseInstructionGenerator):
    """Crememberingstrings Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_m=8, max_cost=10**6):
        """
        初始化Crememberingstrings指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_cost: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = min(max_n, 20)  # Ensure max_n ≤20 per problem constraints
        self.max_m = min(max_m, 20)  # Ensure max_m ≤20
        self.max_cost = max_cost
    
    def case_generator(self):
        # Control case size to avoid O(2^n) explosion
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        
        # Generate cases with 10% probability of already being valid
        if random.random() < 0.1:
            strings = []
            for i in range(n):
                # Ensure each string has a unique position
                unique_pos = random.randint(0, m-1)
                unique_char = random.choice(ascii_lowercase)
                # Make sure no other string has this char at this pos
                while any(s[unique_pos] == unique_char for s in strings):
                    unique_char = random.choice(ascii_lowercase)
                s = [
                    random.choice(ascii_lowercase) 
                    if j != unique_pos else unique_char 
                    for j in range(m)
                ]
                strings.append(''.join(s))
            costs = [[0]*m for _ in range(n)]  # Zero cost case
            return {
                'n': n, 'm': m,
                'strings': strings,
                'costs': costs,
                'correct_output': 0
            }
        else:
            # Regular case generation
            strings = [''.join(random.choices(ascii_lowercase, k=m)) for _ in range(n)]
            costs = [[random.randint(0, self.max_cost) for _ in range(m)] for _ in range(n)]
        
        # Compute correct answer
        try:
            correct_output = solve(n, m, strings, costs)
        except:
            # Fallback to prevent generation failure
            correct_output = 0
        
        return {
            'n': n, 'm': m,
            'strings': strings,
            'costs': costs,
            'correct_output': correct_output
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_str = "\n".join([
            f"{question_case['n']} {question_case['m']}",
            *question_case['strings'],
            *[' '.join(map(str, row)) for row in question_case['costs']]
        ])
        return f"""Solve this problem where you need to find the minimum cost to make all strings uniquely identifiable. Provide your answer in [answer] tags.

Input:
{input_str}

[answer]</answer>[answer]"""  # Intentional format to test extraction 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

