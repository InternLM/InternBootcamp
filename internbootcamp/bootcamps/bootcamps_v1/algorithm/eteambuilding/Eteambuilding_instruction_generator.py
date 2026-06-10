import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EteambuildingInstructionGenerator(BaseInstructionGenerator):
    """Eteambuilding Bootcamp指令生成器"""
    
    def __init__(self, max_n=20, max_m=20, max_k=10):
        """
        初始化Eteambuilding指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_k: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  # 适当扩大测试规模
        self.max_m = max_m
        self.max_k = max_k
    
    def case_generator(self):
        k = random.randint(2, self.max_k)
        n = random.randint(1, self.max_n)
        
        # 允许生成空组（重要修正点）
        c_list = []
        groups = list(range(1, k+1)) + [random.randint(1, k) for _ in range(3)]  # 增加重复概率
        for _ in range(n):
            c_list.append(random.choice(groups))
        
        # 生成唯一边集
        edge_set = set()
        students = list(range(1, n+1))
        for _ in range(min(self.max_m, n*(n-1)//2)):
            a, b = random.sample(students, 2)
            a, b = sorted([a, b])
            edge_set.add((a, b))
        edges = list(edge_set)
        
        return {
            "n": n,
            "m": len(edges),
            "k": k,
            "c_list": c_list,
            "edges": edges,
            "correct_answer": compute_correct_answer(n, len(edges), k, c_list, edges)
        }
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [
            f"{question_case['n']} {question_case['m']} {question_case['k']}",
            ' '.join(map(str, question_case['c_list']))
        ]
        input_lines.extend(f"{a} {b}" for a, b in question_case['edges'])
        input_str = '\n'.join(input_lines)
        prompt = f"""Alice需要选择两个不同的学术组，使得这两个组的所有学生可以被分成两队且每队内没有熟人。请根据以下输入数据计算有效的组对数量，答案格式为[answer]数字[/answer]。

输入格式：
n m k
c_1 c_2 ... c_n
a_1 b_1
...
a_m b_m

输入数据：
{input_str}

请将最终答案放在[answer]标签内。"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

