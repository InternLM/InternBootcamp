import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from heapq import heappush
from heapq import heappop
import random
import re




class CtravellingsalesmanproblemInstructionGenerator(BaseInstructionGenerator):
    """Ctravellingsalesmanproblem Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=15, a_min=0, a_max=1e9, c_min=0, c_max=1e9):
        """
        初始化Ctravellingsalesmanproblem指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            a_min: 参数描述
            a_max: 参数描述
            c_min: 参数描述
            c_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.a_min = a_min
        self.a_max = a_max
        self.c_min = c_min
        self.c_max = c_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        cities = []
        prev_a = -1
        for _ in range(n):
            # 生成保证严格递增的a序列
            new_a = random.randint(max(self.a_min, prev_a + 1), 
                                 max(self.a_max, prev_a + 100))
            new_c = random.randint(self.c_min, self.c_max)
            cities.append((new_a, new_c))
            prev_a = new_a
        
        # 添加随机扰动保证案例多样性
        if random.random() < 0.3:
            cities = sorted(cities, key=lambda x: x[0], reverse=True)[::-1]
        
        correct_answer = self.calculate_min_cost(n, cities)
        return {
            'n': n,
            'cities': cities,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        cities = question_case['cities']
        n = question_case['n']
        input_lines = [f"{ai} {ci}" for ai, ci in cities]
        input_str = '\n'.join([str(n)] + input_lines)
        return f"""城市数据（已按美景值排序）：
{input_str}

请计算最小旅行费用，将最终答案放在[answer]标签内。规则重申：
1. 必须从城市1出发并返回
2. 每个城市访问恰好一次
3. 费用计算规则：max(出发城市c值，目的城市a值 - 出发城市a值)""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_min_cost(n, a):
        a.sort()
        to = [0] * n
        d = [float('inf')] * n
        d[0] = 0
        q = [(0, 0)]
        total_c = sum(c for _, c in a)

        # 预计算每个城市的可达范围
        for i in range(n):
            x, y = a[i]
            l, r = i, n
            while l < r:
                m = (l + r) // 2
                if a[m][0] <= x + y:
                    l = m + 1
                else:
                    r = m
            to[i] = l - 1

        # 动态规划推进
        while q:
            cost, p = heappop(q)
            if cost > d[p]:
                continue

            # 向左扩展
            if p > 0 and d[p-1] > cost:
                d[p-1] = cost
                heappush(q, (cost, p-1))

            # 向右扩展
            if to[p] < n and d[to[p]] > cost:
                d[to[p]] = cost
                heappush(q, (cost, to[p]))

            # 跳跃扩展
            if to[p] + 1 < n:
                new_cost = cost + (a[to[p]+1][0] - a[p][0] - a[p][1])
                if new_cost < d[to[p]+1]:
                    d[to[p]+1] = new_cost
                    heappush(q, (new_cost, to[p]+1))

        return total_c + d[-1]
