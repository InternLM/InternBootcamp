import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class DjonandorbsInstructionGenerator(BaseInstructionGenerator):
    """Djonandorbs Bootcamp指令生成器"""
    
    def __init__(self, max_k=10, max_q=5, max_p=1000, d_max=10000):
        """
        初始化Djonandorbs指令生成器
        
        Args:
            max_k: 参数描述
            max_q: 参数描述
            max_p: 参数描述
            d_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_k = max_k
        self.max_q = max_q
        self.max_p = max_p
        self.d_max = d_max
    
    def case_generator(self):
        k = random.randint(1, self.max_k)
        q = random.randint(1, self.max_q)
        queries = [random.randint(1, self.max_p) for _ in range(q)]

        # Precompute dynamic programming table with correct recurrence
        dp = [[0.0] * (k + 1) for _ in range(self.d_max + 1)]
        dp[0][0] = 1.0

        for d in range(1, self.d_max + 1):
            for ki in range(0, min(k, d) + 1):
                if ki == 0:
                    dp[d][ki] = 0.0
                else:
                    term1 = 0.0
                    if ki - 1 <= (d - 1) and ki - 1 >= 0:
                        term1 = dp[d - 1][ki - 1] * ((k - (ki - 1)) / k)
                    term2 = 0.0
                    if ki <= (d - 1):
                        term2 = dp[d - 1][ki] * (ki / k)
                    dp[d][ki] = term1 + term2

        answers = []
        for p in queries:
            threshold = p / 2000.0
            answer = None
            for candidate_d in range(k, self.d_max + 1):
                if dp[candidate_d][k] >= threshold:
                    answer = candidate_d
                    break
            if answer is None:
                raise ValueError(f"No solution found for p={p}, k={k}")
            answers.append(answer)

        return {
            'k': k,
            'queries': queries,
            'answers': answers
        }
    
    @staticmethod
    def prompt_func(question_case):
        k = question_case['k']
        queries = question_case['queries']
        q = len(queries)
        input_lines = [f"{k} {q}"] + [str(p) for p in queries]
        input_example = '\n'.join(input_lines)

        prompt = f"""Jon Snow needs to collect {k} different types of magical orbs. Each day, one orb appears at the base of the Weirwood tree, with each type equally likely. He wants to determine the minimum number of days he must wait to ensure the probability of collecting at least one of each orb type is at least the specified threshold for each query.

The threshold for the i-th query is p_i/2000. For each query, calculate the smallest number of days required.

Input Format:
The first line contains two integers, k (number of orb types) and q (number of queries).
The next q lines each contain an integer p_i (the threshold parameter for the query).

Output Format:
Output q lines, each containing the minimum number of days for the corresponding query.

Example Input:
{input_example}

Please provide your answers for all queries, each on a new line, enclosed within [answer] and [/answer] tags. For example:

[answer]
{question_case['answers'][0]}
...
[/answer]

Ensure each value is correctly formatted and in order."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

