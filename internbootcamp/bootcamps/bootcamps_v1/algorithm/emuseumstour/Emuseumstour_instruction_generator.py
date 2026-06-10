import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class EmuseumstourInstructionGenerator(BaseInstructionGenerator):
    """Emuseumstour Bootcamp指令生成器"""
    
    def __init__(self, max_n=4, max_m=5, max_d=3):
        """
        初始化Emuseumstour指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            max_d: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_m = max_m
        self.max_d = max_d
    
    def case_generator(self):
        """生成完全符合题目约束的测试案例"""
        # 生成城市数量（包含n=1的边界情况）
        n = random.randint(1, self.max_n)
        
        # 动态计算最大可能道路数
        max_possible_roads = n * (n - 1)
        available_m_upper = min(max_possible_roads, self.max_m)
        m = random.randint(0, available_m_upper) if n > 1 else 0  # n=1时强制m=0
        
        # 生成合法道路集合
        possible_edges = []
        if n > 1:
            possible_edges = [(u, v) for u in range(1, n+1) for v in range(1, n+1) if u != v]
            roads = random.sample(possible_edges, k=m) if m > 0 else []
        else:
            roads = []
        
        # 生成合法博物馆开放时间（保证每个馆至少开放一天）
        d = random.randint(1, self.max_d)
        museums = []
        for _ in range(n):
            while True:
                schedule = ''.join(random.choice('01') for _ in range(d))
                if '1' in schedule:
                    break
            museums.append(schedule)
        
        return {
            'n': n,
            'm': m,
            'd': d,
            'roads': roads,
            'museums': museums,
            'correct_answer': self.compute_solution(n, m, d, roads, museums)
        }
    
    @staticmethod
    def prompt_func(question_case):
        """生成符合题目要求的详细描述"""
        input_lines = [
            f"{question_case['n']} {question_case['m']} {question_case['d']}",
            *[f"{u} {v}" for (u, v) in question_case['roads']],
            *question_case['museums']
        ]
        problem_desc = (
            "You are a tourist in country N with the following configuration:\n"
            f"- Cities: {question_case['n']}\n"
            f"- One-way roads: {question_case['m']}\n"
            f"- Week length: {question_case['d']} days\n\n"
            "Road list:\n" + '\n'.join(f"{u} → {v}" for u, v in question_case['roads']) + "\n\n"
            "Museum schedules (city 1 to n):\n" + '\n'.join(
                f"City {i+1}: {s}" for i, s in enumerate(question_case['museums'])
            ) + "\n\n"
            "Find the maximum distinct museums visitable starting from city 1 on day 1.\n"
            "Format your final answer as [answer]N[/answer] where N is the number."
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_solution(n, m, d, roads, museums):
        """严格实现原题参考算法逻辑"""
        # 邻接表初始化（1-based）
        adj = [[] for _ in range(n+1)]
        rev = [[] for _ in range(n+1)]
        for u, v in roads:
            adj[u].append(v)
            rev[v].append(u)

        # 日期循环处理
        nxt = [(i+1)%d for i in range(d)]
        prev = [(i-1+d)%d for i in range(d)]

        # 第一次DFS确定处理顺序
        visited = [[False]*d for _ in range(n+1)]
        process_stack = []

        for city in range(1, n+1):
            for day in range(d):
                if not visited[city][day]:
                    stack = [(city, day, False)]
                    while stack:
                        x, y, processed = stack.pop()
                        if processed:
                            process_stack.append((x, y))
                            continue
                        if visited[x][y]:
                            continue
                        visited[x][y] = True
                        stack.append((x, y, True))  # 标记为已处理
                        # 处理相邻节点
                        for v in adj[x]:
                            ny = nxt[y]
                            if not visited[v][ny]:
                                stack.append((v, ny, False))

        # 逆向处理强连通分量
        visited = [[False]*d for _ in range(n+1)]
        best = [[0]*d for _ in range(n+1)]
        INIT = 10**9
        best[1][0] = INIT
        max_result = 0

        while process_stack:
            x, y = process_stack.pop()
            if visited[x][y]:
                continue

            component = []
            component_best = 0
            unique_museums = set()
            dfs_stack = [(x, y)]

            # 收集强连通分量节点
            while dfs_stack:
                cx, cy = dfs_stack.pop()
                if visited[cx][cy]:
                    continue
                visited[cx][cy] = True
                component.append((cx, cy))
                component_best = max(component_best, best[cx][cy])

                # 记录未访问的开放博物馆
                if museums[cx-1][cy] == '1' and cx not in unique_museums:
                    unique_museums.add(cx)

                # 逆向遍历
                for u in rev[cx]:
                    py = prev[cy]
                    if not visited[u][py]:
                        dfs_stack.append((u, py))

            # 计算结果
            total = component_best + len(unique_museums)
            for (cx, cy) in component:
                best[cx][cy] = total
                # 更新邻接节点状态
                for v in adj[cx]:
                    nd = nxt[cy]
                    if best[v][nd] < total:
                        best[v][nd] = total
            max_result = max(max_result, total)

        return max_result - INIT
