import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import bisect
import random
from collections import defaultdict
import re




class DeelsInstructionGenerator(BaseInstructionGenerator):
    """Deels Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Deels指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        default_params = {
            'q': 5,
            'max_x': 10**9,
            'min_q': 1,
            'max_q': 20  # Adjusted for manageable case generation
        }
        self.params = {**default_params, **params}
    
    def case_generator(self):
        q = self.params['q']
        max_x = self.params['max_x']
        operations = []
        current_count = defaultdict(int)
        groups = defaultdict(lambda: {'sum': 0, 'elements': []})

        answers = []

        for _ in range(q):
            if not current_count or random.random() < 0.5:
                x = random.randint(1, max_x)
                op_type = '+'
            else:
                available_x = [k for k, v in current_count.items() if v > 0]
                x = random.choice(available_x)
                op_type = '-'

            if op_type == '+':
                i = 0
                while (1 << (i + 1)) <= x:
                    i += 1
                groups[i]['sum'] += x
                bisect.insort(groups[i]['elements'], x)
                current_count[x] += 1
                operations.append(('+', x))
            else:
                i = 0
                while (1 << (i + 1)) <= x:
                    i += 1
                if x in groups[i]['elements']:
                    idx = bisect.bisect_left(groups[i]['elements'], x)
                    if idx < len(groups[i]['elements']) and groups[i]['elements'][idx] == x:
                        groups[i]['elements'].pop(idx)
                        groups[i]['sum'] -= x
                        current_count[x] -= 1
                        if current_count[x] == 0:
                            del current_count[x]
                operations.append(('-', x))

            S = 0
            ans = 0
            for i in range(31):
                group = groups.get(i, {'sum': 0, 'elements': []})
                if not group['elements']:
                    continue
                cnt = len(group['elements'])
                ans += cnt
                min_x = group['elements'][0]
                if min_x > 2 * S:
                    ans -= 1
                S += group['sum']
            answers.append(ans)

        case = {
            'operations': [{'type': op[0], 'x': op[1]} for op in operations],
            'answers': answers
        }
        return case
    
    @staticmethod
    def prompt_func(question_case) -> str:
        q = len(question_case['operations'])
        input_lines = [f"{q}"]
        for op in question_case['operations']:
            input_lines.append(f"{op['type']} {op['x']}")
        input_str = '\n'.join(input_lines)
        prompt = f"""Vasya is managing a set of eels and performing a series of operations. Each operation is either adding (+) or removing (-) an eel of specific weight. After each operation, compute the danger of the current set of eels. The danger is defined as the maximum possible number of dangerous battles that can occur if all eels fight until one remains.

Rules:
- A battle between two eels with weights a and b (a ≤ b) is dangerous if b ≤ 2*a.
- When eels fight, the larger (or equal) one eats the smaller, and its weight becomes a+b. The process repeats until one eel remains. The danger is the maximum count of dangerous battles possible across all fight sequences.

Task:
Given the sequence of operations, output the danger value after each operation.

Input format:
- The first line has an integer q (number of operations).
- The next q lines each are "+ x" (add eel of weight x) or "- x" (remove an eel of weight x; guaranteed to exist).

Output format:
- q integers, each on a new line, indicating the danger after each operation.

Input:
{input_str}

Please provide your answer as q integers, each on a new line, enclosed within [answer] and [/answer]. For example:
[answer]
0
1
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

