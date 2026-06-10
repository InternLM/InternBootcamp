import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re
from collections import deque




class EpermutationrecoveryInstructionGenerator(BaseInstructionGenerator):
    """Epermutationrecovery Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Epermutationrecovery指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = params.get('n_range', (1, 10))
        self.mask_prob = params.get('mask_prob', 0.4)
        self.unsolve_prob = params.get('unsolve_prob', 0.3)
    
    def case_generator(self):
        if random.random() < self.unsolve_prob:
            return self._generate_unsolvable_case()
        return self._generate_solvable_case()
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        next_values = ' '.join(map(str, question_case['next']))
        return f"""根据给定的部分next值，重建合法排列。规则：
1. next_i表示i之后第一个大于p_i的索引（1-based）
2. 若无更大元素则设为{n+1}
3. 丢失值用-1表示

输入：
n = {n}
next = [{next_values}]

请将最终答案用[answer]包裹，示例：
[answer]3 1 2[/answer] 或 [answer]-1[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_solvable_case(self):
        n = random.randint(*self.n_range)
        p = list(range(1, n+1))
        random.shuffle(p)
        next_list = self.compute_next(p)
        masked_next = [
            x if random.random() < self.mask_prob else -1
            for x in next_list
        ]
        return {'n': n, 'next': masked_next}

    def _generate_unsolvable_case(self):
        conflict_types = [
            self._create_cycle_conflict,
            self._create_order_conflict,
            self._create_range_conflict
        ]
        for _ in range(50):
            creator = random.choice(conflict_types)
            case = creator()
            if case and not self.check_solvable(case['n'], case['next']):
                return case
        return {'n': 3, 'next': [3, 4, -1]}

    def _create_cycle_conflict(self):
        n = random.randint(3, 6)
        next_list = [-1]*n
        for i in range(n-1):
            next_list[i] = i+2  # 创建循环依赖
        next_list[-1] = 1
        return {'n': n, 'next': next_list}

    def _create_order_conflict(self):
        n = random.randint(4, 6)
        next_list = [-1]*n
        next_list[0] = n+1  # 无效的next值
        for i in range(1, n-1):
            next_list[i] = i+2
        return {'n': n, 'next': next_list}

    def _create_range_conflict(self):
        n = 5
        return {'n': n, 'next': [3, 6, 4, 6, -1]}

    @staticmethod
    def compute_next(p):
        n = len(p)
        next_arr = []
        for i in range(n):
            min_j = n + 1
            for j in range(i+1, n):
                if p[j] > p[i]:
                    min_j = j + 1
                    break
            next_arr.append(min_j)
        return next_arr

    @staticmethod
    def check_solvable(n, next_list):
        next_array = [x-1 if x != -1 else -1 for x in next_list]
        graph = [[] for _ in range(n)]
        stack = []

        # 构建图结构
        for i in range(n):
            if 0 <= next_array[i] < n:
                graph[i].append(next_array[i])

            while stack and (next_array[stack[-1]] == -1 or next_array[stack[-1]] <= i):
                stack.pop()
            if stack:
                graph[i].append(stack[-1])
            if next_array[i] != -1 and next_array[i] != n:
                stack.append(i)

        # 拓扑排序检测
        in_degree = [0]*n
        for u in range(n):
            for v in graph[u]:
                if 0 <= v < n:
                    in_degree[v] += 1

        queue = deque([u for u in range(n) if in_degree[u] == 0])
        visited = 0

        while queue:
            u = queue.popleft()
            visited += 1
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        return visited == n
