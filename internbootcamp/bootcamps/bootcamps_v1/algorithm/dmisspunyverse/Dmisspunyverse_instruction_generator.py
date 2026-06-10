import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
from sys import setrecursionlimit




class DmisspunyverseInstructionGenerator(BaseInstructionGenerator):
    """Dmisspunyverse Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dmisspunyverse指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = params.get('max_n', 10)
        self.min_n = params.get('min_n', 2)
        self.max_value = params.get('max_value', 100)
        setrecursionlimit(1000000)  # 统一设置递归深度
    
    def case_generator(self):
        """生成合法测试用例，确保m <= n"""
        while True:
            n = random.randint(self.min_n, self.max_n)
            m = random.randint(1, n)
            b = [random.randint(0, self.max_value) for _ in range(n)]
            w = [random.randint(0, self.max_value) for _ in range(n)]
            edges = self.generate_tree_edges(n)
            
            try:
                # 使用类方法调用避免实例属性访问
                correct_answer = self.solve_case(n, m, b, w, edges)
                return {
                    'n': n,
                    'm': m,
                    'b': b,
                    'w': w,
                    'edges': edges,
                    'correct_answer': correct_answer
                }
            except Exception as e:
                # 打印调试信息
                print(f"Error generating case: {e}")
                continue
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """增强提示模板，明确答案格式"""
        input_lines = [
            f"{question_case['n']} {question_case['m']}",
            ' '.join(map(str, question_case['b'])),
            ' '.join(map(str, question_case['w'])),
            '\n'.join(f"{u} {v}" for u, v in question_case['edges'])
        ]
        return f"""Solve the tree partition problem. You are given:
- A tree with {question_case['n']} nodes
- Bees and wasps counts for each node
- Need to partition into exactly {question_case['m']} villages

Calculate the maximum villages where wasps win (strict majority).

Input format:
{input_lines[0]}
{input_lines[1]}
{input_lines[2]}
{input_lines[3]}

Output a single integer within [answer]...[/answer]. Example: [answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_tree_edges(self, n):
        """生成合法的树结构，节点编号从1开始"""
        if n == 1:
            return []
        edges = []
        parents = list(range(n))
        for i in range(1, n):
            parents[i] = random.randint(0, i-1)
        # 转换为1-based节点编号
        for i in range(1, n):
            u = parents[i] + 1
            v = i + 1
            edges.append((u, v))
        random.shuffle(edges)
        return edges

    @staticmethod
    def solve_case(n, m, b, w, edges):
        """树形DP实现，修复状态初始化问题"""
        # 构建邻接表 (0-based)
        adj = [[] for _ in range(n)]
        for u, v in edges:
            adj[u-1].append(v-1)
            adj[v-1].append(u-1)

        a = [w[i] - b[i] for i in range(n)]

        # DP状态数组 (max_m+2防止越界)
        max_m = m
        dp = [[(-1, -float('inf'))] * (max_m + 2) for _ in range(n)]
        sz = [0] * n

        def dfs(parent, u):
            sz[u] = 1
            dp[u][1] = (0, a[u])  # 初始状态

            for v in adj[u]:
                if v == parent:
                    continue
                dfs(u, v)

                # 合并子树状态
                current_max = min(sz[u], max_m)
                child_max = min(sz[v], max_m)
                ndp = [(-1, -float('inf'))] * (current_max + child_max + 1)

                for i in range(1, current_max + 1):
                    if dp[u][i][0] == -1:
                        continue
                    for j in range(1, child_max + 1):
                        if dp[v][j][0] == -1:
                            continue

                        # 合并分支选项
                        merged_k = i + j - 1
                        if merged_k <= max_m:
                            total_win = dp[u][i][0] + dp[v][j][0]
                            total_sum = dp[u][i][1] + dp[v][j][1]
                            if (total_win > ndp[merged_k][0]) or \
                               (total_win == ndp[merged_k][0] and total_sum > ndp[merged_k][1]):
                                ndp[merged_k] = (total_win, total_sum)

                        # 独立分支选项
                        separate_k = i + j
                        if separate_k <= max_m:
                            add_win = 1 if dp[v][j][1] > 0 else 0
                            total_win = dp[u][i][0] + dp[v][j][0] + add_win
                            total_sum = dp[u][i][1]
                            if (total_win > ndp[separate_k][0]) or \
                               (total_win == ndp[separate_k][0] and total_sum > ndp[separate_k][1]):
                                ndp[separate_k] = (total_win, total_sum)

                # 更新状态数组
                for k in range(len(ndp)):
                    if k > max_m:
                        continue
                    if ndp[k][0] > dp[u][k][0] or \
                       (ndp[k][0] == dp[u][k][0] and ndp[k][1] > dp[u][k][1]):
                        dp[u][k] = ndp[k]
                sz[u] += sz[v]

        dfs(-1, 0)
        max_win, sum_total = dp[0][m]

        # 处理根节点的剩余值
        if sum_total > 0:
            max_win += 1
        return max(max_win, 0)  # 保证非负
