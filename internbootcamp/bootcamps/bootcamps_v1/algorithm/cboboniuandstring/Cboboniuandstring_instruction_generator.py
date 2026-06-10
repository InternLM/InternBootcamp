import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class CboboniuandstringInstructionGenerator(BaseInstructionGenerator):
    """Cboboniuandstring Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cboboniuandstring指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = params.get('n_min', 1)
        self.n_max = params.get('n_max', 5)
        self.string_length_min = params.get('string_length_min', 1)
        self.string_length_max = params.get('string_length_max', 10)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        strings = []
        a_list = []
        b_list = []
        for _ in range(n):
            length = random.randint(self.string_length_min, self.string_length_max)
            s = ''.join(random.choices(['B', 'N'], k=length))
            strings.append(s)
            a_list.append(s.count('N'))
            b_list.append(s.count('B'))
        
        max_a = max(a_list) if a_list else 0
        max_b = max(b_list) if b_list else 0
        best_max = float('inf')
        best_x, best_y = 0, 0

        # Generate comprehensive candidate points
        x_candidates = set(a_list)
        for dx in range(-2, 3):
            x_candidate = max_a + dx
            if x_candidate >= 0:
                x_candidates.add(x_candidate)
        x_candidates.add(0)

        y_candidates = set(b_list)
        for dy in range(-2, 3):
            y_candidate = max_b + dy
            if y_candidate >= 0:
                y_candidates.add(y_candidate)
        y_candidates.add(0)

        # Evaluate all candidate combinations
        for x in x_candidates:
            for y in y_candidates:
                if x == 0 and y == 0:
                    continue
                current_max = 0
                for a, b in zip(a_list, b_list):
                    if x <= a and y <= b:
                        current = max(a - x, b - y)
                    elif x <= a or y <= b:
                        current = abs(a - x) + abs(b - y)
                    else:
                        current = max(x - a, y - b)
                    current_max = max(current_max, current)
                if current_max < best_max or (current_max == best_max and (x + y < best_x + best_y)):
                    best_max = current_max
                    best_x, best_y = x, y

        return {
            'n': n,
            'strings': strings,
            'a_list': a_list,
            'b_list': b_list,
            'x_opt': best_x,
            'y_opt': best_y,
            'max_distance': best_max
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_example = "\n".join(question_case['strings'])
        prompt = f"""You are given a problem involving BN-strings and their distances. 

Problem Description:
Boboniu defines the distance between two BN-strings s and t as the minimum number of operations to make s similar to t. Two BN-strings are similar if they have the same length and can be permuted to match each other. The allowed operations include adding/removing characters 'B' or 'N', adding/removing substrings "BN" or "NB", and so on. The distance is the minimal number of these operations required.

Your task is to find a non-empty BN-string t that minimizes the maximum distance to each of the given input strings. 

Input:
The input consists of {question_case['n']} BN-strings:

{input_example}

Output Requirements:
Output two lines:
1. The minimal possible maximum distance.
2. A BN-string t that achieves this distance. If multiple solutions exist, output any.

Format your answer as follows, enclosed within [answer] and [/answer] tags:

[answer]
<max_distance>
<t>
[/answer]

For example, if the answer is a maximum distance of 1 and the string "BN", the response should be:

[answer]
1
BN
[/answer]

Now, find the solution for the provided input."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

