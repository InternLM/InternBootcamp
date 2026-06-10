import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random




class BformingteamsInstructionGenerator(BaseInstructionGenerator):
    """Bformingteams Bootcamp指令生成器"""
    
    def __init__(self, n_min=2, n_max=100, m_max=100):
        """
        初始化Bformingteams指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            m_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = n_min
        self.n_max = n_max
        self.m_max = m_max
    
    def case_generator(self):
        max_attempts = 1000  # 防止无限循环
        for _ in range(max_attempts):
            try:
                n = random.randint(self.n_min, self.n_max)
                m_max = min(self.m_max, n)
                if m_max < 1:
                    m_max = 1  # 确保至少一个边
                m = random.randint(1, m_max)

                edges = []
                # 生成环或链结构
                if m == n:
                    # 生成一个环
                    cycle = list(range(1, n + 1))
                    for i in range(n):
                        a = cycle[i]
                        b = cycle[(i + 1) % n]
                        edges.append((a, b) if a < b else (b, a))
                    edges = sorted(edges)
                else:
                    # 生成一个链，需要确保m+1 <=n
                    if m + 1 > n:
                        continue  # 当前n无法生成m条边，跳过
                    chain_nodes = list(range(1, m + 2))  # m+1个节点
                    for i in range(m):
                        edges.append((chain_nodes[i], chain_nodes[i + 1]))

                # 验证边数和度数约束
                if len(edges) != m:
                    continue
                degree = {}
                valid = True
                for a, b in edges:
                    degree[a] = degree.get(a, 0) + 1
                    degree[b] = degree.get(b, 0) + 1
                    if degree[a] > 2 or degree[b] > 2:
                        valid = False
                        break
                if not valid:
                    continue
                # 确保边无重复
                unique_edges = set(tuple(sorted(e)) for e in edges)
                if len(unique_edges) != m:
                    continue

                # 计算正确答案
                pairs = [set() for _ in range(n)]
                for a, b in edges:
                    ai, bi = a - 1, b - 1
                    pairs[ai].add(bi)
                    pairs[bi].add(ai)
                rest = set(range(n))
                bench = 0
                mod = 0
                while rest:
                    start = rest.pop()
                    prev = start
                    ct = 1
                    curr = pairs[prev].pop() if pairs[prev] else None
                    processed = {start}
                    while curr is not None and curr not in processed:
                        processed.add(curr)
                        rest.discard(curr)
                        pairs[curr].discard(prev)
                        next_curr = pairs[curr].pop() if pairs[curr] else None
                        prev, curr = curr, next_curr
                        ct += 1
                    if curr == start and ct > 1:  # 环处理
                        bench += ct % 2
                    else:  # 链处理
                        mod += ct
                mod %= 2
                correct = bench + mod
                return {
                    'n': n,
                    'm': m,
                    'edges': edges,
                    'correct_output': correct
                }
            except Exception as e:
                continue
        # 多次尝试后仍无法生成则返回默认值
        return {
            'n': 5,
            'm': 4,
            'edges': [(1,2),(2,4),(5,3),(1,4)],
            'correct_output': 1
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        m = question_case['m']
        edges = '\n'.join(f"{a} {b}" for a, b in question_case['edges'])
        return f"""You are organizing a football game with {n} students. Students have mutual archenemies (each has ≤2). Split into two equal teams with no enemies in the same team. If impossible, some must bench. Find the minimal number to bench.

Input:
{n} {m}
{edges}

Output: A single integer. Place your answer within [answer] tags, e.g., [answer]1[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

