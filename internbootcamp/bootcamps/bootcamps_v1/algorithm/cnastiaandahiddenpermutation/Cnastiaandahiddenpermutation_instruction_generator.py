import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CnastiaandahiddenpermutationInstructionGenerator(BaseInstructionGenerator):
    """Cnastiaandahiddenpermutation Bootcamp指令生成器"""
    
    def __init__(self, min_n=3, max_n=10):
        """
        初始化Cnastiaandahiddenpermutation指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        p = list(range(1, n + 1))
        random.shuffle(p)
        queries = self.simulate_queries(p)
        return {
            'n': n,
            'permutation': p,
            'queries': queries
        }
    
    @staticmethod
    def prompt_func(question_case):
        queries = question_case['queries']
        queries_text = []
        for t, i, j, x, res in queries:
            queries_text.append(f"? {t} {i} {j} {x} → {res}")
        queries_str = "\n".join(queries_text)
        return f"""Nastia has a hidden permutation of length {question_case['n']}. The following queries were made and their responses are given:

{queries_str}

Determine the hidden permutation and provide your answer as "! p1 p2 ... pn" enclosed within [answer] tags. For example: [answer]! 1 2 3 4[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def simulate_queries(self, p):
        queries = []
        n = len(p)

        def ask(t, i, j, x):
            i_index = i - 1  # Convert to 0-based
            j_index = j - 1
            pi = p[i_index]
            pj = p[j_index]
            if t == 1:
                res = max(min(x, pi), min(x + 1, pj))
            elif t == 2:
                res = min(max(x, pi), max(x + 1, pj))
            else:
                res = -1
            queries.append((t, i, j, x, res))
            return res

        a = [0] * n
        for i in range(0, n - 1, 2):
            x = ask(2, i + 1, (i + 1) + 1, 1)
            y = ask(1, i + 1, (i + 1) + 1, n - 1)

            if x == 2 and ask(1, i + 1, (i + 1) + 1, 1) == 1:
                a[i + 1] = 1
                if y == n - 1 and ask(2, i + 1, (i + 1) + 1, n - 1) == n:
                    a[i] = n
                else:
                    a[i] = y
                continue

            if y == n - 1 and ask(2, i + 1, (i + 1) + 1, n - 1) == n:
                a[i] = n
                a[i + 1] = x
                continue

            check = ask(2, (i + 1) + 1, i + 1, x)
            if check == x + 1:
                a[i] = x
                a[i + 1] = y
            else:
                a[i] = y
                a[i + 1] = x

        if n % 2 == 1:
            last = set(range(1, n + 1)) - set(a[:n-1])
            a[-1] = last.pop()

        return queries
