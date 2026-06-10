import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import deque

# === 源文件中的全局函数 ===

def calculate_answer(n, m, d, roads, schedules):
    adj = [[] for _ in range(n)]
    for u, v in roads:
        adj[u].append(v)
    open_table = [ [c == '1' for c in s] for s in schedules ]

    max_museums = 0

    visited = {}  # (current city, day in week) -> max museums count

    initial_museums = 0
    if open_table[0][0]:
        initial_museums = 1

    queue = deque()
    # State: (city, day, visited_museums_bitmask)
    initial_state = (0, 0, initial_museums, 1 << 0 if open_table[0][0] else 0)
    queue.append(initial_state)
    visited[(0, 0)] = (initial_museums, initial_state[3])

    max_museums = initial_museums

    while queue:
        u, t, count, mask = queue.popleft()

        next_t = (t + 1) % d

        for v in adj[u]:
            new_mask = mask
            new_count = count
            # Check if we can visit v's museum at next_t day
            if open_table[v][next_t] and not (mask & (1 << v)):
                new_count += 1
                new_mask |= 1 << v
            key = (v, next_t)
            if key not in visited or visited[key][0] < new_count or (visited[key][0] == new_count and visited[key][1] | new_mask != visited[key][1]):
                visited[key] = (new_count, new_mask)
                queue.append((v, next_t, new_count, new_mask))
                if new_count > max_museums:
                    max_museums = new_count

    return max_museums


class CmuseumstourInstructionGenerator(BaseInstructionGenerator):
    """Cmuseumstour Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cmuseumstour指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = {
            'n': params.get('n', 4),
            'm': params.get('m', 5),
            'd': params.get('d', 3),
        }
        # Ensure parameters are within BFS processing limits
        max_n = 10  # Adjust based on performance testing
        max_d = 7
        self.params['n'] = min(self.params['n'], max_n)
        self.params['d'] = min(self.params['d'], max_d)
        # Ensure m does not exceed possible roads
        max_possible_m = self.params['n'] * (self.params['n'] - 1)
        self.params['m'] = min(self.params['m'], max_possible_m)
    
    def case_generator(self):
        n = self.params['n']
        m = self.params['m']
        d = self.params['d']

        # Generate all possible valid roads
        possible_roads = []
        for u in range(n):
            for v in range(n):
                if u != v:
                    possible_roads.append((u, v))
        
        # Adjust m if it exceeds possible roads
        if not possible_roads:
            m = 0
        else:
            m = min(m, len(possible_roads))
        
        # Randomly sample unique roads
        roads = random.sample(possible_roads, m) if possible_roads else []

        # Generate schedules ensuring capital has at least one open day
        schedules = []
        for i in range(n):
            if i == 0:  # Capital city
                while True:
                    s = ''.join(random.choice(['0', '1']) for _ in range(d))
                    if '1' in s:
                        break
                schedules.append(s)
            else:
                s = ''.join(random.choice(['0', '1']) for _ in range(d))
                schedules.append(s)

        # Calculate correct answer with retry logic
        max_retry = 3
        correct_answer = 0
        for _ in range(max_retry):
            try:
                correct_answer = calculate_answer(n, m, d, roads, schedules)
                break
            except:
                continue

        return {
            'n': n,
            'm': m,
            'd': d,
            'roads': roads,
            'schedules': schedules,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_desc = [
            f"{question_case['n']} {question_case['m']} {question_case['d']}",
            '\n'.join(f"{u+1} {v+1}" for u, v in question_case['roads']),
            '\n'.join(question_case['schedules'])
        ]
        input_example = '\n'.join(input_desc)

        problem_text = f"""\
You are planning a museum tour in a country with one-way roads. Starting in city 1 on week day 1, maximize the number of distinct museums visited. Each road takes one night to travel. Museums have weekly schedules.

Input format:
- First line: n m d
- Next m lines: u v (one-way roads)
- Next n lines: d digits (0/1) per city's schedule

Write your answer as [answer]N[/answer], replacing N with the maximum number.

Input:
{input_example}

What's the maximum number of distinct museums you can visit?"""
        return problem_text 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

