import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def correct_solution(n, m, d, g, r):
    d_sorted = sorted(d)
    # Check if any adjacent islands exceed g distance
    for i in range(1, len(d_sorted)):
        if d_sorted[i] - d_sorted[i-1] > g:
            return -1
    m = len(d_sorted)
    INF = float('inf')
    dp = [[INF] * (g + 1) for _ in range(m)]
    dp[0][0] = 0
    heap = []
    import heapq
    heapq.heappush(heap, (0, 0, 0))  # (cycles, u, rem)

    while heap:
        cycles, u, rem = heapq.heappop(heap)
        if cycles > dp[u][rem]:
            continue
        for dv in [-1, 1]:
            v = u + dv
            if 0 <= v < m:
                distance = abs(d_sorted[u] - d_sorted[v])
                new_rem = rem + distance
                if new_rem > g:
                    continue
                if new_rem == g:
                    new_cycles = cycles + 1
                    new_r = 0
                else:
                    new_cycles = cycles
                    new_r = new_rem
                if dp[v][new_r] > new_cycles:
                    dp[v][new_r] = new_cycles
                    heapq.heappush(heap, (new_cycles, v, new_r))
    min_time = INF
    for i in range(m):
        time_needed = n - d_sorted[i]
        if time_needed <= g and dp[i][0] != INF:
            total_time = dp[i][0] * (g + r) + time_needed
            if total_time < min_time:
                min_time = total_time
    return min_time if min_time != INF else -1


class EnastyaandunexpectedguestRewardCalculator(BaseRewardCalculator):
    """Enastyaandunexpectedguest奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        numbers = re.findall(r'-?\d+', last_match)
        if not numbers:
            return None
        try:
            return int(numbers[-1])
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        m = identity['m']
        d = identity['d']
        g = identity['g']
        r = identity['r']
        correct = correct_solution(n, m, d, g, r)
        return solution == correct
    
    # 其他额外方法

