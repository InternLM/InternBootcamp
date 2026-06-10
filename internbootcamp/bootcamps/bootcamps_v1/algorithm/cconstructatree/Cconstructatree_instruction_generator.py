import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from collections import defaultdict
import re




class CconstructatreeInstructionGenerator(BaseInstructionGenerator):
    """Cconstructatree Bootcamp指令生成器"""
    
    def __init__(self, max_n=1000, **params):
        """
        初始化Cconstructatree指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.params = params
    
    def case_generator(self):
        n = random.randint(2, self.max_n)
        generate_possible = random.choice([True, False])
        
        s_min = 2 * n - 1
        s_max = n * (n + 1) // 2
        
        if generate_possible:
            s = random.randint(s_min, s_max)
        else:
            if random.random() < 0.5:
                s = random.randint(1, s_min - 1)
            else:
                s = s_max + random.randint(1, 1000)
        
        if s < s_min or s > s_max:
            return {'n': n, 's': s, 'possible': False}
        else:
            solution = self.generate_solution(n, s)
            if solution['possible']:
                return {
                    'n': n,
                    's': s,
                    'possible': True,
                    'p_array': solution['p_array'],
                    'k': solution['k']
                }
            else:
                return {'n': n, 's': s, 'possible': False}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        s = question_case['s']
        problem_desc = f"""Misha wants to construct a rooted tree with {n} vertices where the root is vertex 1. The tree must satisfy that the sum of the sizes of all subtrees equals {s}. The branching coefficient (maximum number of children any vertex has) must be as small as possible. 

Your task is to determine if such a tree exists. If it exists, output "Yes" followed by the parent array. Otherwise, output "No". 

The parent array should list the parent of vertices 2 to {n}, space-separated. For example, if the parents are 1 and 1 for vertices 2 and 3 respectively, output "1 1". 

Please format your answer as follows:

[answer]
Yes
1 1 
[/answer]

or 

[answer]
No
[/answer]

Ensure your answer is enclosed within [answer] and [/answer] tags."""
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_solution(n, s):
        if s < 2 * n -1 or s > n * (n + 1) // 2:
            return {'possible': False}

        left = 0
        right = n - 1
        d_final = None
        answer_r = None

        while right - left > 1:
            mid = (left + right) // 2
            possible, d = Cconstructatreebootcamp.go(mid, n, s)
            if possible:
                right = mid
            else:
                left = mid

        possible, d = Cconstructatreebootcamp.go(right, n, s)
        if not possible:
            possible_left, d_left = Cconstructatreebootcamp.go(left, n, s)
            if possible_left:
                right = left
                d = d_left
            else:
                return {'possible': False}

        p_array = Cconstructatreebootcamp.construct_p(n, right, d)
        children = defaultdict(list)
        for i in range(2, n + 1):
            parent = p_array[i-2]
            children[parent].append(i)
        max_degree = max(len(v) for v in children.values()) if children else 0

        return {
            'possible': True,
            'p_array': p_array,
            'k': right,
            'max_degree': max_degree
        }

    @staticmethod
    def go(deg, n, s):
        he = 2
        curs = s
        curs -= 1  # Root node's contribution
        already = 0
        can = deg
        d = [0] * (n + 1)
        d[1] = 1  # Depth of root is 1

        for i in range(2, n + 1):
            if already == can:
                he += 1
                already = 0
                can *= deg

            remaining_nodes = n - i
            mx_term = (2 * he + remaining_nodes) * (remaining_nodes) // 2

            if curs <= he + mx_term:
                already += 1
                d[i] = he
                curs -= he
            else:
                he += 1
                d[i] = he
                curs -= he

        return curs == 0, d

    @staticmethod
    def construct_p(n, r, d):
        can = [r] * (n + 2)
        le = 1
        p = [0] * (n + 1)

        for i in range(2, n + 1):
            while le <= n and can[le] == 0:
                le += 1

            while le < i and d[le] + 1 < d[i]:
                le += 1

            p[i] = le
            can[le] -= 1

        return p[2:n+1]
