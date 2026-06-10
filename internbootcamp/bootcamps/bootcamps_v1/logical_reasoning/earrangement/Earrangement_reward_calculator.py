import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque

# === 源文件中的全局函数 ===

def is_dag(edges, n_nodes):
    adj = [[] for _ in range(n_nodes + 1)]
    in_degree = [0] * (n_nodes + 1)
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    queue = deque()
    for node in range(1, n_nodes + 1):
        if in_degree[node] == 0:
            queue.append(node)
    visited = 0
    while queue:
        u = queue.popleft()
        visited += 1
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return visited == n_nodes

def calculate_count(n, ls, pref):
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        if dp[mask] == 0:
            continue
        cnt = bin(mask).count('1')
        for i in range(n):
            if pref[i] != -1 and pref[i] != (n - cnt - 1):
                continue
            if (ls[i] & mask) != ls[i]:
                continue
            if (mask & (1 << i)) != 0:
                continue
            new_mask = mask | (1 << i)
            dp[new_mask] += dp[mask]
    return dp[(1 << n) - 1]

def solve_puzzle(n, y, m, constraints):
    original_y = y
    y -= 2000
    if y <= 0:
        return "The times have changed"
    ls = [0] * n
    for u, v in constraints:
        ai = u - 1
        bi_seat = v - 1
        ls[ai] |= 1 << bi_seat
    pref = [-1] * n
    for i in range(n):
        while True:
            pref[i] += 1
            if pref[i] >= n:
                return "The times have changed"
            current_pref = pref[:i+1] + [-1] * (n - i - 1)
            current_count = calculate_count(n, ls, current_pref)
            if current_count < y:
                y -= current_count
            else:
                break
    arrangement = [str(p + 1) for p in pref]
    return ' '.join(arrangement)


class EarrangementRewardCalculator(BaseRewardCalculator):
    """Earrangement奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 使用正则表达式匹配最后一个[answer]标签中的内容
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        # 处理可能的换行和多余空格
        last_answer = re.sub(r'\s+', ' ', last_answer).strip()
        return last_answer
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        # 标准化solution的格式
        solution = solution.strip().lower()
        # 获取正确解
        try:
            correct = solve_puzzle(
                identity['n'],
                identity['y'],
                identity['m'],
                identity['constraints']
            )
            # 处理两种可能的结果
            if correct == "The times have changed":
                return solution == "the times have changed"
            else:
                # 将答案转换为统一格式（如去除多余空格）
                correct_clean = re.sub(r'\s+', ' ', correct).strip()
                solution_clean = re.sub(r'\s+', ' ', solution).strip()
                return correct_clean == solution_clean
        except:
            return solution == "the times have changed"
    
    # 其他额外方法

