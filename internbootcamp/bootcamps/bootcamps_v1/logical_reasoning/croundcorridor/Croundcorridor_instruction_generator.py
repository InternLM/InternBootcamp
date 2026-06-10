import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import re
import random
from math import gcd




class CroundcorridorInstructionGenerator(BaseInstructionGenerator):
    """Croundcorridor Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Croundcorridor指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n = params.get('n', 4)
        self.m = params.get('m', 6)
        self.q = params.get('q', 3)
    
    def case_generator(self):
        n = self.n
        m = self.m
        q = self.q

        g = gcd(n, m)
        total = (n * m) // g
        tn = total // n  # m // g
        tm = total // m  # n // g
        current_gcd = gcd(tn, tm)
        gc = (tn * tm) // current_gcd

        queries = []

        for _ in range(q):
            s_x = random.choice([1, 2])
            e_x = random.choice([1, 2])

            s_y = random.randint(1, n) if s_x == 1 else random.randint(1, m)
            e_y = random.randint(1, n) if e_x == 1 else random.randint(1, m)

            # Calculate processed coordinates
            x = (s_y - 1) * tn if s_x == 1 else (s_y - 1) * tm
            y = (e_y - 1) * tn if e_x == 1 else (e_y - 1) * tm

            block_x = x // gc
            block_y = y // gc

            answer = 'YES' if block_x == block_y else 'NO'
            queries.append({
                'input': [s_x, s_y, e_x, e_y],
                'answer': answer
            })

        case = {
            'n': n,
            'm': m,
            'q': q,
            'queries': queries
        }
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        q = question_case['q']
        queries = question_case['queries']

        prompt = (
            f"Croundcorridor is in a large circular corridor divided into an inner area and an outer area. The inner area is divided into {n} sectors, numbered (1,1) to (1,{n}) clockwise. The outer area is divided into {m} sectors, numbered (2,1) to (2,{m}) clockwise. There are walls between adjacent sectors of the same area, but no walls between inner and outer sectors. A wall is always present at the 12 o'clock position.\n\n"
            f"Croundcorridor wants to determine if he can move from one sector to another. You will be given {q} queries. For each query, you must output YES if movement is possible and NO otherwise.\n\n"
            "Queries:\n"
        )

        for idx, query in enumerate(queries, 1):
            s_x, s_y, e_x, e_y = query['input']
            start_area = "inner" if s_x == 1 else "outer"
            end_area = "inner" if e_x == 1 else "outer"
            prompt += (
                f"Query {idx}: Start at sector ({s_x},{s_y}) in the {start_area} area. End at sector ({e_x},{e_y}) in the {end_area} area.\n"
            )

        prompt += (
            "\nOutput your answers as a space-separated list within [answer] tags. Example: [answer]YES NO YES[/answer]"
        )
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

