import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from typing import Dict
from typing import Any




class EcleverfatratInstructionGenerator(BaseInstructionGenerator):
    """Ecleverfatrat Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, **kwargs):
        """
        初始化Ecleverfatrat指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**kwargs)
        self.max_n = max_n
    
    def case_generator(self) -> Dict[str, Any]:
        n = random.randint(1, self.max_n)
        strategy = random.choice([0, 1, 2])  # 0: random, 1: force Cerealguy, 2: force Fat Rat
        
        a = []
        w = []
        
        if strategy == 1:  # Generate cases where Cerealguy is possible
            a = [random.randint(5, 100) for _ in range(n)]
            w = []
            for i in range(n):
                row_size = n - i
                if i == 0:  # First row (i=1 in problem terms)
                    # Ensure a_i >= w_i for all scales in the first row
                    w_row = [random.randint(1, a_val) for a_val in a]
                else:
                    w_row = [random.randint(1, 100) for _ in range(row_size)]
                w.append(w_row)
            # Adjust last row to potentially allow sum >= w
            if n > 1:
                total_upper = sum(a)
                w[-1] = [random.randint(1, total_upper)]
        elif strategy == 2:  # Generate cases where Fat Rat is likely
            a = [random.randint(1, 50) for _ in range(n)]
            w = []
            for i in range(n):
                row_size = n - i
                if i == 0:  # First row
                    # Ensure a_i < w_i for all scales
                    w_row = [random.randint(a_val + 1, 100) for a_val in a]
                else:
                    w_row = [random.randint(1, 100) for _ in range(row_size)]
                w.append(w_row)
        else:  # Random generation
            a = [random.randint(1, 100) for _ in range(n)]
            w = []
            for i in range(n):
                row_size = n - i
                w_row = [random.randint(1, 100) for _ in range(row_size)]
                w.append(w_row)
        
        correct_answer = self.compute_correct_answer(n, a, w)
        return {
            'n': n,
            'a': a,
            'w': w,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        a = ' '.join(map(str, question_case['a']))
        w_rows = []
        for row in question_case['w']:
            w_rows.append(' '.join(map(str, row)))
        w_description = '\n'.join(w_rows)
        prompt = f"""As a programming expert, solve the problem and format your answer within [answer] tags.

Problem:
The Fat Rat and Cerealguy are betting on whether oats will reach the Fat Rat's claws. The structure has {n} rows of scales. Each row's scales have weight capacities. Follow the breaking rules to determine the outcome.

Input:
- Line 1: {n}
- Line 2: {a}
- Next {n} lines:
{w_description}

Rules:
- Scales break if oats ≥ capacity. Contents fall to possible scales below.
- Output "Cerealguy" if any oats reach the Fat Rat, else "Fat Rat".

Provide your answer as [answer]result[/answer], exactly one of the two options."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_correct_answer(n, a_list, w_list):
        memo = {}

        def dfs(i, j, l, r):
            key = (i, j, l, r)
            if key in memo:
                return memo[key]
            if j > r or (i + j - 1) < l or l > r:
                memo[key] = 0
                return 0
            if i == 1:
                a_j = a_list[j-1]
                w_ij = w_list[i-1][j-1]
                result = a_j if a_j >= w_ij else 0
                memo[key] = result
                return result
            max_sum = 0
            for k in range(l-1, r + 1):
                left = dfs(i-1, j, l, k)
                right = dfs(i-1, j+1, k+1, r)
                current_sum = left + right
                if current_sum > max_sum:
                    max_sum = current_sum
            w_ij = w_list[i-1][j-1]
            result = max_sum if max_sum >= w_ij else 0
            memo[key] = result
            return result

        total_sum = dfs(n, 1, 1, n)
        return "Cerealguy" if total_sum > 0 else "Fat Rat"
