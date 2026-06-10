import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import deque




class EluckypermutationInstructionGenerator(BaseInstructionGenerator):
    """Eluckypermutation Bootcamp指令生成器"""
    
    def __init__(self, max_n=10**9, valid_case_prob=0.5):
        """
        初始化Eluckypermutation指令生成器
        
        Args:
            max_n: 参数描述
            valid_case_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.valid_case_prob = valid_case_prob
    
    def case_generator(self):
        if random.random() < self.valid_case_prob:
            # Generate valid cases (k <= possible permutations)
            n = random.choice([
                random.randint(1, 12),
                random.randint(13, 20)  # Ensure coverage of n>=13 cases
            ])
            max_fact = self._factorials[min(n, 13)]
            k = random.randint(1, max_fact)
        else:
            # Generate invalid cases (k > possible permutations)
            n = random.randint(1, self.max_n)
            max_fact = self._factorials[min(n, 13)] if n <= 13 else 0
            k = random.randint(max(1, max_fact + 1), 10**9)
        return {'n': n, 'k': k}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        k = question_case['k']
        problem_desc = f"""Solve the following lucky permutation problem:
- Lucky numbers contain only 4 and 7 digits (e.g. 4, 7, 44, 747)
- Find the number of positions i (1-based) in the {k}-th lex permutation of 1..{n}
  where both i and a_i are lucky numbers
- If there are fewer than {k} permutations, output -1

Format your answer as [answer]N[/answer] where N is the result."""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def _calculate_expected(cls, n, k_input):
        # Generate all lucky numbers up to n
        lucky = []
        q = deque([0])
        while q:
            u = q.popleft()
            if u > n:
                continue
            if u > 0:
                lucky.append(u)
            q.append(u * 10 + 4)
            q.append(u * 10 + 7)
        lucky = sorted(lucky)

        L = min(13, n)
        s = n - L + 1
        if s < 1:
            s = 1

        # Count lucky indices before s
        pre_count = sum(1 for x in lucky if x < s)

        # Check if permutation is possible
        if L == 0 or k_input > cls._factorials[L]:
            return -1 if L > 0 else 0

        # Generate permutation suffix
        suffix = list(range(s, n+1))
        k = k_input - 1
        perm = []
        while suffix and k > 0:
            fact = cls._factorials[len(suffix)-1]
            idx = 0
            while (idx + 1) * fact <= k:
                idx += 1
            perm.append(suffix[idx])
            del suffix[idx]
            k -= idx * fact
        perm += suffix

        # Count valid positions in permutation
        count = 0
        for i in range(len(perm)):
            pos = s + i
            if pos > n:
                break
            if pos in lucky and perm[i] in lucky:
                count += 1

        return pre_count + count if len(perm) == L else -1
