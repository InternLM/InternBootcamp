import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EarrangementInstructionGenerator(BaseInstructionGenerator):
    """Earrangement Bootcamp指令生成器"""
    
    def __init__(self, max_n=16, **params):
        """
        初始化Earrangement指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        super().__init__(**params)
    
    def case_generator(self):
        # 生成教授数n，确保不超过题目要求的16
        n = random.randint(1, min(16, self.max_n))
        seats = list(range(1, n + 1))
        # 生成m的取值范围：0到min(100, n*(n-1))
        max_possible_m = n * (n - 1)
        m_max = min(100, max_possible_m)
        m = random.randint(0, m_max)
        edges = []
        # 生成m对约束，允许重复和无效约束
        for _ in range(m):
            ai, bi = random.choices(seats, k=2)
            if ai != bi:
                edges.append((ai, bi))
        # 去重（仅提高生成效率，但保留重复的可能性）
        edges = list(set(edges))  # 根据题目要求，重复约束不影响结果，但减少无效尝试
        m = len(edges)
        # 检查约束是否形成DAG
        valid_dag = is_dag(edges, n)
        # 确定y的取值范围
        if not valid_dag:
            # 约束无效时，任何年份都应返回错误
            y = random.randint(2001, 2001 + 100)
        else:
            try:
                ls = [0] * n
                for u, v in edges:
                    ai = u - 1
                    bi_seat = v - 1
                    ls[ai] |= 1 << bi_seat
                pref = [-1] * n
                total = calculate_count(n, ls, pref)
                if total == 0:
                    valid_dag = False  # 虽然约束是DAG，但无解
                else:
                    # 50%概率生成有效年份，50%生成超限年份
                    if random.random() < 0.5:
                        y = 2000 + random.randint(1, total)
                    else:
                        y = 2000 + total + random.randint(1, 3)
            except:
                valid_dag = False
        # 最终生成案例
        return {
            'n': n,
            'y': y,
            'm': m,
            'constraints': edges
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        y = question_case['y']
        m = question_case['m']
        constraints = question_case['constraints']
        problem = (
            f"In the year 2500, the GUC graduation ceremony requires professors to be seated with specific seniority rules.\n"
            f"There are {n} professors (seniority 1 to {n}) and {m} seat relations.\n"
            f"Determine the seating arrangement for year {y} considering lexicographical order.\n"
            f"Constraints:\n" + 
            '\n'.join(f"{ai} {bi}" for ai, bi in constraints) + 
            "\n\nOutput the arrangement as space-separated numbers or state 'The times have changed' within [answer] tags. "
            "Example:\n[answer]1 2 3[/answer]\nOR\n[answer]The times have changed[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

