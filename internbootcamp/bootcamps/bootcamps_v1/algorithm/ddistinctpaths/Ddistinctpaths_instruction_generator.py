import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7


class DdistinctpathsInstructionGenerator(BaseInstructionGenerator):
    """Ddistinctpaths Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, max_k=10):
        """
        初始化Ddistinctpaths指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_k = max_k
    
    def case_generator(self):
        n, m = 0, 0
        for _ in range(100):  # Retry to get valid n, m
            n = random.randint(1, self.max_n)
            m = random.randint(1, self.max_m)
            if n + m <= 11:
                break
        k = random.randint(max(n + m -1, 1), self.max_k)
        grid_full = self.generate_valid_full_grid(n, m, k)
        if not grid_full:
            grid_initial = [[0]*m for _ in range(n)]
        else:
            grid_initial = []
            for row in grid_full:
                new_row = []
                for val in row:
                    if random.random() < 0.3:  # 30% chance to retain color
                        new_row.append(val)
                    else:
                        new_row.append(0)
                grid_initial.append(new_row)
        # Compute expected solution
        expected = self.compute_solution(n, m, k, grid_initial)
        return {
            'n': n,
            'm': m,
            'k': k,
            'grid': grid_initial,
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case):
        grid = question_case['grid']
        n = question_case['n']
        m = question_case['m']
        k = question_case['k']
        grid_str = '\n'.join(' '.join(map(str, row)) for row in grid)
        return f"""You are given a {n}x{m} grid. Some cells are colored (1 to {k}) and others are 0 (uncolored). Your task is to count the number of ways to color all 0-cells such that every path from the top-left to the bottom-right (moving only right or down) has all distinct colors. Output the count modulo 1e9+7.

Input:
{n} {m} {k}
{grid_str}

The output must be the number of valid ways modulo 1e9+7. Place your final answer within [answer] tags, e.g., [answer]12345[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_valid_full_grid(self, n, m, k):
        grid = [[0 for _ in range(m)] for _ in range(n)]
        for i in range(n):
            for j in range(m):
                used = set()
                if i > 0:
                    used.add(grid[i-1][j])
                if j > 0:
                    used.add(grid[i][j-1])
                available = [c for c in range(1, k+1) if c not in used]
                if not available:
                    return None
                grid[i][j] = min(available)
        return grid

    @staticmethod
    def compute_solution(n, m, k, grid):
        if n + m > 11 or (n + m - 1) > k:
            return 0
        grid = [[cell-1 if cell !=0 else -1 for cell in row] for row in grid]
        a = [[-1]*(m+2) for _ in range(n+2)]
        for i in range(n):
            for j in range(m):
                a[i+1][j+1] = grid[i][j] if grid[i][j] != -1 else -1
        lim2 = [[0]*(m+2) for _ in range(n+2)]
        s = 0
        for i in range(1, n+1):
            for j in range(1, m+1):
                if a[i][j] != -1:
                    s |= 1 << a[i][j]
                    if i < n:
                        lim2[i][j] |= 1 << a[i][j]
                    if j < m:
                        lim2[i][j] |= 1 << a[i][j]
        for i in range(n, 0, -1):
            for j in range(m, 0, -1):
                lim2[i][j] |= lim2[i+1][j] | lim2[i][j+1]
                if a[i][j] != -1 and (lim2[i][j] & (1 << a[i][j])):
                    return 0
        v = []
        for color in range(k):
            if not (s & (1 << color)):
                v.append(color)
        if not v:
            return 1
        # DFS to compute answer
        memo = {}
        def dfs(x, y, cnt, lim):
            if x > n:
                return 1
            if y > m:
                return dfs(x+1, 1, cnt, lim)
            key = (x, y, cnt, tuple(map(tuple, lim)))
            if key in memo:
                return memo[key]
            current_lim = lim[x-1][y] | lim[x][y-1]
            total = 0
            for color in range(k):
                if a[x][y] != -1 and color != a[x][y]:
                    continue
                if current_lim & (1 << color):
                    continue
                if lim2[x][y] & (1 << color):
                    continue
                if not (s & (1 << color)):
                    if a[x][y] == -1 and (cnt >= len(v) or color > v[cnt]):
                        continue
                new_lim = [row[:] for row in lim]
                new_lim[x][y] = current_lim | (1 << color)
                new_cnt = cnt
                if a[x][y] == -1 and not (s & (1 << color)):
                    if color == v[cnt]:
                        new_cnt = min(len(v)-1, cnt + 1)
                res = dfs(x, y+1, new_cnt, new_lim)
                if a[x][y] == -1 and color in v and cnt < len(v) and color == v[cnt]:
                    total = (total + res * (len(v) - cnt)) % MOD
                else:
                    total = (total + res) % MOD
            memo[key] = total
            return total
        lim_init = [[0]*(m+2) for _ in range(n+2)]
        result = dfs(1, 1, 0, lim_init)
        return result
