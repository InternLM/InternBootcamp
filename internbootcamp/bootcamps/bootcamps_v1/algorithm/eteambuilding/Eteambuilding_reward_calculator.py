import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def compute_correct_answer(n, m, k, c_list, edges):
    group_edges = defaultdict(list)
    cross_edges = []
    mark = defaultdict(bool)
    
    # 学生编号1-based处理
    c = [0] * (n + 1)
    for i in range(1, n+1):
        c[i] = c_list[i-1]
    
    dsu = DSU(2*(n+2))  # 每个节点分拆为两个
    
    # 分离同组边和跨组边
    for a, b in edges:
        if c[a] == c[b]:
            group_edges[c[a]].append((a, b))
        else:
            u, v = sorted([c[a], c[b]])
            cross_edges.append((u, v, a, b))
    
    # 处理同组边（标记矛盾组）
    for group in group_edges:
        conflict = False
        cp = len(dsu.history)
        for a, b in group_edges[group]:
            # 检查合并是否产生矛盾
            dsu.merge(a, b + n)
            dsu.merge(b, a + n)
            if dsu.find(a) == dsu.find(a + n):
                conflict = True
                break
        if conflict:
            mark[group] = True
        dsu.rollback(cp)  # 回滚到处理前的状态
    
    # 排序跨组边（关键修正点）
    cross_edges.sort(key=lambda x: (x[0], x[1]))
    
    # 统计无效组对
    total_pairs = k * (k - 1) // 2
    invalid_pairs = 0
    tot_marked = sum(mark.values())
    invalid_pairs += tot_marked * (k - tot_marked) + tot_marked * (tot_marked - 1) // 2
    
    # 处理跨组边（修正排序逻辑）
    i = 0
    while i < len(cross_edges):
        j = i
        current_u = cross_edges[i][0]
        current_v = cross_edges[i][1]
        while j < len(cross_edges) and cross_edges[j][0:2] == (current_u, current_v):
            j += 1
        
        if mark[current_u] or mark[current_v]:
            invalid_pairs += 1
            i = j
            continue
        
        conflict = False
        cp = len(dsu.history)
        for idx in range(i, j):
            _, _, a, b = cross_edges[idx]
            dsu.merge(a, b + n)
            dsu.merge(b, a + n)
            if dsu.find(a) == dsu.find(a + n) or dsu.find(b) == dsu.find(b + n):
                conflict = True
                break
        
        if conflict:
            invalid_pairs += 1
        dsu.rollback(cp)
        i = j
    
    return total_pairs - invalid_pairs



# === 源文件中的其他类 ===

class DSU:
    def __init__(self, size):
        self.parent = list(range(size))
        self.size = [1] * size
        self.history = []
    
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]  # 路径压缩
            x = self.parent[x]
        return x
    
    def merge(self, x, y):
        fx = self.find(x)
        fy = self.find(y)
        if fx == fy:
            return
        if self.size[fx] < self.size[fy]:
            fx, fy = fy, fx
        self.history.append((fy, fx))  # 记录合并顺序
        self.parent[fy] = fx
        self.size[fx] += self.size[fy]
    
    def rollback(self, checkpoint):
        while len(self.history) > checkpoint:
            fy, fx = self.history.pop()
            self.parent[fy] = fy
            self.size[fx] -= self.size[fy]


class EteambuildingRewardCalculator(BaseRewardCalculator):
    """Eteambuilding奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 强化正则匹配（支持含空格的情况）
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

