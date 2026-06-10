import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CmuseumstourRewardCalculator(BaseRewardCalculator):
    """Cmuseumstour奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

