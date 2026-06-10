import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import math
from itertools import combinations




class FaupontrougeInstructionGenerator(BaseInstructionGenerator):
    """Faupontrouge Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Faupontrouge指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        # Default parameters with dynamic generation capability
        self.n = params.get('n', 4)
        self.m = params.get('m', 2)
        self.k = params.get('k', 1)
        self.s = params.get('s', 'abac')

        # Ensure parameters are valid
        self.n = len(self.s)
        if not 1 <= self.m <= self.n:
            raise ValueError("m must be between 1 and string length")
        max_k = math.comb(self.n-1, self.m-1)
        if self.k > max_k:
            raise ValueError(f"k exceeds maximum possible value {max_k}")
    
    def case_generator(self):
        """Generate a valid puzzle case ensuring adequate combinations"""
        # Generate random case parameters with constraints
        import random
        import string
        
        # Random string length between 4-8 for manageability
        n = random.randint(4, 8)
        s = ''.join(random.choices(string.ascii_lowercase, k=n))
        
        # Ensure m is at least 1 and less than n
        m = random.randint(1, min(3, n-1))
        
        # Calculate maximum possible k
        max_k = math.comb(n-1, m-1)
        k = random.randint(1, max(1, max_k//2))  # Use conservative k
        
        return {
            'n': n,
            'm': m,
            'k': k,
            's': s
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        params = question_case
        return f"""VK's building has string '{params['s']}' (length {params['n']}). Split it into {params['m']} rooms. For each split, take the lex-smallest substring. Sort these minimal substrings in reverse lex order. What's the {params['k']}-th element?

Output must be wrapped in [answer] and [/answer] tags. Example: [answer]abc[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def find_in_trie(cls, nodes, idx):
        result = []
        cur = 0
        have = 0
        while True:
            have += nodes[cur].interm
            if have > idx:
                return ''.join(result)
            found = False
            for i in range(26):
                next_node = nodes[cur].nxt[i]
                if next_node == -1:
                    continue
                if have + nodes[next_node].have > idx:
                    result.append(chr(ord('a') + i))
                    cur = next_node
                    found = True
                    break
                else:
                    have += nodes[next_node].have
            if not found:
                break
        return ''.join(result)

    @classmethod
    def check_valid(cls, s, k, candidate, m):
        n = len(s)
        l = len(candidate)
        cont = [-1] * n

        # Precompute continuation points
        for i in range(n):
            pos = i
            while pos < n and pos - i < l and s[pos] == candidate[pos - i]:
                pos += 1
            if pos < n and pos - i < l and s[pos] < candidate[pos - i]:
                cont[i] = -1
            elif pos == n or pos - i == l:
                cont[i] = pos
            else:
                cont[i] = pos + 1 if pos < n else -1

        # DP table initialization
        dp = [[0]*m for _ in range(n)]
        if cont[0] != -1 and cont[0] <= n:
            end = cont[0] - 1
            if end < n:
                dp[end][0] = 1

        for i in range(n-1):
            for j in range(m):
                dp[i+1][j] = min(k, dp[i+1][j] + dp[i][j])

            if cont[i+1] == -1:
                continue

            for j in range(m-1):
                if dp[i][j] == 0:
                    continue
                next_pos = cont[i+1] - 1
                if next_pos >= n or j+1 >= m:
                    continue
                dp[next_pos][j+1] = min(k, dp[next_pos][j+1] + dp[i][j])

        return dp[n-1][m-1] >= k
