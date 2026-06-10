import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import defaultdict
from math import ceil




class CrestoregraphInstructionGenerator(BaseInstructionGenerator):
    """Crestoregraph Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, **params):
        """
        初始化Crestoregraph指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        super().__init__(**params)
    
    def case_generator(self):
        # Generate valid or invalid cases
        generate_valid = random.random() < 0.7  # 70% valid, 30% invalid
        n = random.randint(2, self.max_n)
        valid = True

        # Generate initial valid layers (s)
        s = [1]
        remaining = n - 1
        while remaining > 0:
            next_s = random.randint(1, remaining)
            s.append(next_s)
            remaining -= next_s

        # Calculate minimal required k
        max_k = 0
        for i in range(len(s)-1):
            current_s = s[i]
            next_s = s[i+1]
            required_k = ceil(next_s / current_s) + (i != 0)
            max_k = max(max_k, required_k)
        k = max_k

        # Generate d array
        d = []
        for i, count in enumerate(s):
            d.extend([i] * count)
        random.shuffle(d)

        # Introduce invalid conditions if needed
        if not generate_valid:
            invalid_type = random.choice([0, 1, 2, 3])
            if invalid_type == 0:
                # Break s[0] to invalid count
                s[0] = 0
                d = []
                for i, cnt in enumerate(s):
                    d.extend([i] * cnt)
                d[random.randint(0, len(d)-1)] = 0  # Ensure at least one 0
            elif invalid_type == 1 and max_k > 1:
                # Reduce k to make insufficient
                k = random.randint(1, max_k - 1)
            elif invalid_type == 2 and len(s) > 1:
                # Disrupt d array hierarchy
                max_d = len(s) - 1
                if max_d + 1 < n:
                    idx = random.randint(0, len(d)-1)
                    d[idx] = max_d + 1
            elif invalid_type == 3 and len(s) > 2:
                # Make a layer exceed parent capacity
                i = random.randint(1, len(s)-2)
                s[i+1] = s[i] * (k - 1) + 1
                d = []
                for layer, cnt in enumerate(s):
                    d.extend([layer] * cnt)
                random.shuffle(d)
        
        return {'n': n, 'k': k, 'd': d}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        k = question_case['k']
        d = question_case['d']
        input_lines = [f"{n} {k}", ' '.join(map(str, d))]
        input_str = '\n'.join(input_lines)
        prompt = f"""Valera had an undirected connected graph without self-loops or multiple edges, where each vertex has at most {k} edges. He recorded the shortest distances from one vertex to all others in array d. Your task is to determine if the graph can be restored. If not, output -1. Otherwise, output the number of edges followed by the edges. Format your answer within [answer] and [/answer].
Input:
{input_str}"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

