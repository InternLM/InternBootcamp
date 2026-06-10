import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DfafaandancientalphabetInstructionGenerator(BaseInstructionGenerator):
    """Dfafaandancientalphabet Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, p_zero=0.2):
        """
        初始化Dfafaandancientalphabet指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            p_zero: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        Initialize the bootcamp with parameters for generating puzzle cases.

        :param max_n: Maximum length of the words (default 5)
        :param max_m: Maximum size of the alphabet (default 5)
        :param p_zero: Probability of a character being erased (0) (default 0.2)
        """
        self.max_n = max_n
        self.max_m = max_m
        self.p_zero = p_zero
    
    def case_generator(self):
        """
        Generate a puzzle instance with random n, m, S1, and S2.
        """
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        A = []
        B = []
        for _ in range(n):
            # Generate A with possible zeros
            if random.random() < self.p_zero:
                A.append(0)
            else:
                A.append(random.randint(1, m))
        for _ in range(n):
            # Generate B with possible zeros
            if random.random() < self.p_zero:
                B.append(0)
            else:
                B.append(random.randint(1, m))
        
        return {
            'n': n,
            'm': m,
            'A': A,
            'B': B
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """
        Format the question case into a textual prompt with instructions.
        """
        n = question_case['n']
        m = question_case['m']
        A = ' '.join(map(str, question_case['A']))
        B = ' '.join(map(str, question_case['B']))
        prompt = f"""You are tasked with solving a puzzle involving ancient Dfafaandancientalphabet symbols. Two words S1 and S2 of equal length were found, but some symbols are erased (denoted by 0). Each erased symbol can be replaced with any integer from 1 to m. Calculate the probability that S1 is lexicographically greater than S2 and provide the result modulo 10^9+7.

Input Format:
- First line: n m (length of words and alphabet size)
- Second line: {A}
- Third line: {B}

Rules:
1. A word x is lexicographically greater than y if there exists a position where x has a larger character than y, and all preceding characters are equal.
2. 0 represents an erased symbol, which can be replaced by any integer from 1 to m.
3. The result must be expressed as P × Q⁻¹ mod (10⁹+7), where P/Q is the reduced fraction of the probability.

Output your answer within [answer] and [/answer], for example: [answer]123456789[/answer].

Now, solve the following case and provide your answer:"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_correct_answer(n, m, A, B):
        """
        Compute the correct answer based on the problem's reference solution.
        """
        mod = 10**9 + 7

        # Calculate nwilds for total wildcards after each position
        nwilds = [0]
        for i in reversed(range(n)):
            nwilds.append(nwilds[-1] + (A[i] == 0) + (B[i] == 0))
        nwilds.reverse()
        totwilds = nwilds[0]
        del nwilds[0]

        ways = [0] * (n + 1)

        for i in reversed(range(n)):
            a = A[i]
            b = B[i]
            if a == 0 and b == 0:
                above = (m - 1) * m // 2
                term1 = above * pow(m, nwilds[i], mod) % mod
                term2 = m * ways[i + 1] % mod
                ways[i] = (term1 + term2) % mod
            elif a == 0:
                current_b = b
                above = (m - current_b) if current_b <= m else 0
                term1 = above * pow(m, nwilds[i], mod) % mod
                term2 = ways[i + 1] % mod
                ways[i] = (term1 + term2) % mod
            elif b == 0:
                current_a = a
                above = current_a - 1
                term1 = above * pow(m, nwilds[i], mod) % mod
                term2 = ways[i + 1] % mod
                ways[i] = (term1 + term2) % mod
            else:
                if b > a:
                    ways[i] = 0
                elif b < a:
                    ways[i] = pow(m, nwilds[i], mod) % mod
                else:
                    ways[i] = ways[i + 1] % mod

        P = ways[0] % mod
        Q = pow(m, totwilds, mod)
        Q_inv = pow(Q, mod - 2, mod) if Q != 0 else 0
        return (P * Q_inv) % mod
