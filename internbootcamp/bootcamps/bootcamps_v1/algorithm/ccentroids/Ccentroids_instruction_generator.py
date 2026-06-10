import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CcentroidsInstructionGenerator(BaseInstructionGenerator):
    """Ccentroids Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=20):
        """
        初始化Ccentroids指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        edges = self.generate_random_tree(n)
        correct_answer = self.solve_problem(n, edges)
        return {
            'n': n,
            'edges': edges,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        edges_str = '\n'.join(f"{u} {v}" for u, v in question_case['edges'])
        prompt = f"""你是一名网络结构工程师，负责优化一个树形结构的网络节点。你的任务是通过最多一次边的替换操作，使得某个特定节点成为网络的重心。树的重心定义如下：移除该节点后，剩下的每个连通块的大小都不超过原树节点数的一半。边替换操作是指删除一条边并添加一条新边，替换后仍保持树的结构。你需要确定每个节点是否可以通过最多一次这样的操作成为重心。

输入格式：
第一行是一个整数n，表示节点的数量。接下来的n-1行每行两个整数，表示一条边的两个端点。

你的任务是为每个节点i（从1到n），输出1或0，表示是否可以通过最多一次边替换使其成为重心。输出为一个由空格分隔的n个数字组成的字符串。

请按照输入示例的格式进行解答，并将最终答案放置在[answer]和[/answer]标签之间。例如，若正确输出是1 1 1，则你的回答应为：
[answer]1 1 1[/answer]

当前的问题实例：
n = {question_case['n']}
边列表：
{edges_str}"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def generate_random_tree(n):
        if n == 1:
            return []
        edges = []
        for i in range(2, n+1):
            p = random.randint(1, i-1)
            edges.append((p, i))
        random.shuffle(edges)
        return edges

    @staticmethod
    def solve_problem(n, edges):
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        # 第一次DFS寻找重心
        siz = [0]*(n+1)
        res = float('inf')
        rt = 0
        def dfs1(x, F):
            nonlocal res, rt
            siz[x] = 1
            mx = 0
            for y in adj[x]:
                if y == F:
                    continue
                dfs1(y, x)
                siz[x] += siz[y]
                mx = max(mx, siz[y])
            mx = max(mx, n - siz[x])
            if mx < res or (mx == res and x < rt):
                res = mx
                rt = x
        dfs1(1, 0)

        # 第二次DFS建立父节点关系
        siz = [0]*(n+1)
        parent = {}
        def dfs2(x, F):
            parent[x] = F
            siz[x] = 1
            for y in adj[x]:
                if y == F:
                    continue
                dfs2(y, x)
                siz[x] += siz[y]
        dfs2(rt, 0)

        # 获取直接子节点
        sub = []
        for y in adj[rt]:
            if parent[y] == rt:  # 关键修正：确保只处理子节点
                sub.append((siz[y], y))
        sub.sort(reverse=True, key=lambda x: x[0])

        ans = [0]*(n+1)
        ans[rt] = 1

        # 递归求解答案
        def solve(x, F, sum_val, pre):
            if sum_val <= n//2:
                ans[x] = 1
            for i in range(min(2, len(sub))):
                s, node = sub[i]
                if node == pre:
                    continue
                if (n - siz[x] - s) <= n//2:
                    ans[x] = 1
            for y in adj[x]:
                if y == F:
                    continue
                solve(y, x, sum_val, pre)

        # 遍历所有子节点
        for y in adj[rt]:
            if parent[y] != rt:  # 关键修正：过滤非子节点
                continue
            solve(y, rt, n - siz[y], y)

        return ans[1:n+1]
