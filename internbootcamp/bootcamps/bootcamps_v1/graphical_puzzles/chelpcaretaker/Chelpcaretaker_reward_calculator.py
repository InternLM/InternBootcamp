import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class ChelpcaretakerRewardCalculator(BaseRewardCalculator):
    """Chelpcaretaker奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[\/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        answer_content = matches[-1].strip()
        lines = [line.strip() for line in answer_content.split('\n') if line.strip()]
        if len(lines) < 1:
            return None
        try:
            k = int(lines[0])
        except ValueError:
            return None
        layout = lines[1:]
        return {'k': k, 'layout': layout}
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        n = identity['n']
        m = identity['m']
        user_k = solution['k']
        user_layout = solution['layout']

        if len(user_layout) != n:
            return False
        for row in user_layout:
            if len(row) != m:
                return False

        correct_k, _ = solve_turboplow(n, m)
        if user_k != correct_k:
            return False

        cells = defaultdict(list)
        for i in range(n):
            for j in range(m):
                char = user_layout[i][j]
                if char != '.':
                    cells[char].append((i, j))

        all_coords = []
        for char, coords in cells.items():
            if len(coords) != 5:
                return False
            if not is_valid_t_shape(coords):
                return False
            all_coords.extend(coords)

        if len(all_coords) != len(set(all_coords)):
            return False

        return True
    
    # 其他额外方法

