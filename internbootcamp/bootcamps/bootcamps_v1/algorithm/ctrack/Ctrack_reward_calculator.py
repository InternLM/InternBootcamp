import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from heapq import heappop
from heapq import heappush

# === 源文件中的全局函数 ===

def manhattan(r1, c1, r2, c2):
    return abs(r1 - r2) + abs(c1 - c2)

def solve(n, m, k, mat):
    start = None
    end = None
    for i in range(n):
        for j in range(m):
            if mat[i][j] == 'S':
                start = (i, j)
            elif mat[i][j] == 'T':
                end = (i, j)
    if not start or not end:
        return "-1"
    br, bc = start
    er, ec = end

    heap = []
    initial_priority = manhattan(br, bc, er, ec)
    heappush(heap, (initial_priority, '', 0, br, bc, 0, ''))
    ha = {i: {j: set() for j in range(m)} for i in range(n)}

    while heap:
        priority, path, steps, r, c, cu, used_str = heappop(heap)
        if (r, c) == (er, ec):
            return path
        if used_str in ha[r][c]:
            continue
        ha[r][c].add(used_str)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < m:
                ch = mat[nr][nc]
                if ch == 'S':
                    continue
                new_steps = steps + 1
                new_priority = new_steps + manhattan(nr, nc, er, ec)
                if ch == 'T':
                    heappush(heap, (new_priority, path, new_steps, nr, nc, cu, used_str))
                else:
                    if ch in used_str:
                        new_used = used_str
                        new_cu = cu
                    else:
                        new_cu = cu + 1
                        if new_cu > k:
                            continue
                        new_used = ''.join(sorted(set(used_str) | {ch}))
                    new_path = path + ch
                    if new_used not in ha[nr][nc]:
                        heappush(heap, (new_priority, new_path, new_steps, nr, nc, new_cu, new_used))
    return "-1"


class CtrackRewardCalculator(BaseRewardCalculator):
    """Ctrack奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        answer = matches[-1].strip().replace('\n', '').replace(' ', '')
        if answer == '-1':
            return '-1'
        if all(c.islower() for c in answer):
            return answer
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['expected_output']
        return solution == expected
    
    # 其他额外方法

