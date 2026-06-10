import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
from collections import defaultdict

# === 源文件中的全局函数 ===

def solve_turboplow(n, m):
    rf = False
    if n > m:
        n, m, rf = m, n, True
    w = -1 if m == 9 else 1
    Z = ((7, 2, 2), (2, 2, 7), (1, 7, 1), (4, 7, 4))
    Zx = []
    for x in range(n):
        current = []
        for i, j, k in Z:
            current.append((i << x, j << x, k << x))
        Zx.append(current)
    q = [tuple([0] * m)]
    d = {q[0]: 0}
    pr = {q[0]: None}

    def put(p, x, y, i, j, k):
        res = False
        pp = list(p)
        for vi, vj, vk in Zx[x]:
            if (i & vi) or (j & vj) or (k & vk):
                continue
            pp[y] = i | vi
            if y + 1 >= m:
                continue
            pp[y+1] = j | vj
            if y + 2 >= m:
                continue
            pp[y+2] = k | vk
            pc = tuple(pp)
            if pc in d:
                continue
            d[pc] = d[p] + 1
            pr[pc] = p
            q.append(pc)
            res = True
        return res

    for p in q:
        jm = m
        im = n
        for j in range(1, m - 1):
            if j > jm:
                break
            if j + 1 >= m:
                continue
            p1, p2, p3 = p[j-1], p[j], p[j+1]
            for i in range(1, n - 1):
                if i > im:
                    break
                if p2 & (3 << i):
                    continue
                if (p1 & (1 << i)) and (p2 & (1 << (i-1))):
                    continue
                if put(p, i-1, j-1, p1, p2, p3) and im == n:
                    im = i + w
                    jm = j - 1

    max_k = -1
    best_key = None
    for key, value in d.items():
        if value > max_k:
            max_k = value
            best_key = key

    if best_key is None:
        return 0, ['.' * m for _ in range(n)]

    r = [['.'] * m for _ in range(n)]
    current = best_key
    l = 'A'
    while pr.get(current) is not None:
        prev = pr[current]
        for y in range(m):
            for x in range(n):
                if (current[y] & (1 << x)) and not (prev[y] & (1 << x)):
                    r[x][y] = l
        current = prev
        l = chr(ord(l) + 1)

    if rf:
        transposed = []
        for col in range(m):
            transposed_row = []
            for row in range(n):
                transposed_row.append(r[row][col])
            transposed.append(''.join(transposed_row))
        r = transposed
    else:
        r = [''.join(row) for row in r]

    return max_k, r

def is_valid_t_shape(coords):
    if len(coords) != 5:
        return False
    min_r = min(r for r, _ in coords)
    min_c = min(c for _, c in coords)
    translated = set((r - min_r, c - min_c) for r, c in coords)
    patterns = [
        {(0, 0), (0, 1), (0, 2), (1, 1), (2, 1)},
        {(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)},
        {(0, 1), (1, 1), (2, 0), (2, 1), (2, 2)},
        {(0, 0), (0, 1), (1, 0), (1, 1), (1, 2)},
    ]
    return translated in patterns


class ChelpcaretakerInstructionGenerator(BaseInstructionGenerator):
    """Chelpcaretaker Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=9, min_m=1, max_m=9):
        """
        初始化Chelpcaretaker指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_m: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_m = min_m
        self.max_m = max_m
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        m = random.randint(self.min_m, self.max_m)
        return {
            'n': n,
            'm': m
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        prompt = f"""Autumn has come to the kingdom of Far Far Away, and Simon the Caretaker needs to store turboplows in a {n}x{m} warehouse. Each turboplow occupies a T-shaped area that can be rotated in any of four directions. The goal is to place the maximum number of turboplows without overlapping.

Your task is to determine the maximum number of turboplows that can fit and provide a valid layout. The first line of output should be the maximum number. The next {n} lines should each contain {m} characters representing the warehouse layout, using '.' for empty cells and successive letters (A, B, etc.) for each turboplow.

Format your answer exactly as follows between [answer] and [/answer]:

[answer]
{{max_number}}
{{row_1}}
{{row_2}}
...
{{row_{n}}}
[/answer]

Example for a 3x3 warehouse:
[answer]
1
AAA
.A.
.A.
[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

