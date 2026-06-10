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

def compute_answer(n_input, m_input, c_list):
    # Correctly map problem's n (number of colors) and m (strip length) to reference code's variables
    m_code = n_input  # Reference code's m represents problem's n (number of colors)
    n_code = m_input  # Reference code's n represents problem's m (strip length)

    C = [x - 1 for x in c_list]
    
    # Compress consecutive duplicates
    if not C:
        return 0
    C2 = [C[0]]
    for c in C[1:]:
        if C2[-1] != c:
            C2.append(c)
    new_n = len(C2)
    
    # Check if compressed length exceeds 2*m_code (problem's n)
    if new_n > 2 * m_code:
        return 0
    
    pos = [[] for _ in range(m_code)]
    for i in range(new_n):
        c = C2[i]
        if c >= m_code or c < 0:
            return 0
        pos[c].append(i)
    
    # Verify all colors are present
    for color in range(m_code):
        if not pos[color]:
            return 0
    
    DP = [[1] * (new_n + 1) for _ in range(new_n + 1)]
    
    for le in range(1, new_n + 1):
        for i in range(new_n - le + 1):
            j = i + le
            min_color = min(C2[i:j])
            min_indices = [p for p in range(i, j) if C2[p] == min_color]
            if not min_indices:
                DP[i][j] = 0
                continue
            
            first = min(min_indices)
            last = max(min_indices)
            
            # Calculate left part
            left = 0
            for k in range(i, first + 1):
                left = (left + DP[i][k] * DP[k][first]) % MOD
            
            # Calculate right part
            right = 0
            for k in range(last + 1, j + 1):
                right = (right + DP[last + 1][k] * DP[k][j]) % MOD
            
            # Calculate middle parts between occurrences of min_color
            middle = 1
            color_positions = pos[min_color]
            for idx in range(len(color_positions) - 1):
                prev = color_positions[idx]
                next_p = color_positions[idx + 1]
                if prev < i or next_p >= j:
                    continue
                middle = (middle * DP[prev + 1][next_p]) % MOD
            
            DP[i][j] = (left * right % MOD) * middle % MOD
    
    return DP[0][new_n]


class F2longcolorfulstripInstructionGenerator(BaseInstructionGenerator):
    """F2longcolorfulstrip Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=10):
        """
        初始化F2longcolorfulstrip指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        # Ensure valid problem constraints: n >=1, m >=n
        n = random.randint(1, self.max_n)
        m = random.randint(n, self.max_m)
        
        # Generate initial c list containing all colors 1..n
        c = list(range(1, n+1))
        # Add remaining elements randomly
        if m > n:
            c += [random.randint(1, n) for _ in range(m - n)]
        # Shuffle to create random configuration
        random.shuffle(c)
        
        return {
            'n': n,
            'm': m,
            'c': c
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        c = question_case['c']
        c_str = ' '.join(map(str, c))
        problem = f"""You are a programming competition participant. Solve the following problem and enclose your answer within [answer] and [/answer] tags.

Problem:
Calculate the number of valid ways Alice could have painted the strip. The initial strip is color 0, and each step repaints a segment to a new color. The result must match the given configuration.

Input:
The first line contains two integers n and m: {n} {m}.
The second line contains {m} integers: {c_str}.

Output:
The number of valid ways modulo 998244353. Provide your answer inside [answer] tags."""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

