import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CpetyaandexamInstructionGenerator(BaseInstructionGenerator):
    """Cpetyaandexam Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, min_T=1, max_T=50, a_min=1, a_max=5, b_min=3, b_max=8):
        """
        初始化Cpetyaandexam指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            min_T: 参数描述
            max_T: 参数描述
            a_min: 参数描述
            a_max: 参数描述
            b_min: 参数描述
            b_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.min_T = min_T
        self.max_T = max_T
        self.a_min = a_min
        self.a_max = a_max
        self.b_min = b_min
        self.b_max = b_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        T = random.randint(self.min_T, self.max_T)
        
        a = random.randint(self.a_min, self.a_max)
        b = random.randint(self.b_min, self.b_max)
        while b <= a:
            b = random.randint(self.b_min, self.b_max)
        
        types = [random.choice([0, 1]) for _ in range(n)]
        t_list = [random.randint(0, T) for _ in range(n)]
        
        # 添加更多边界案例：全easy/全hard问题
        if random.random() < 0.2:
            types = [0] * n
        elif random.random() < 0.2:
            types = [1] * n
        
        # 确保至少有一个有效案例
        while all(t > T for t in t_list):
            t_list = [random.randint(0, T) for _ in range(n)]
        
        correct_answer = self.solve_case(n, T, a, b, types, t_list)
        
        return {
            'n': n,
            'T': T,
            'a': a,
            'b': b,
            'types': types,
            't_list': t_list,
            'correct_answer': correct_answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        params = question_case
        problem_desc = (
            "Petya has to solve math problems in an exam. The exam lasts {T} minutes with {n} problems. "
            "Easy problems take {a} minutes, hard ones take {b} minutes. Each problem becomes mandatory at a specific time. "
            "If Petya leaves at time s, he must have solved all problems with mandatory time ≤ s. Your task is to determine the maximum points he can earn.\n\n"
            "Problem Details:\n"
            "- Problem types (0=easy, 1=hard): {types}\n"
            "- Mandatory times: {t_list}\n\n"
            "Format your answer as: [answer]X[/answer], where X is the maximum points."
        ).format(
            n=params['n'],
            T=params['T'],
            a=params['a'],
            b=params['b'],
            types=params['types'],
            t_list=params['t_list']
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_case(n, T, a, b, types, times):
        combined = sorted(zip(times, types), key=lambda x: (x[0], x[1]))
        sorted_times = [x[0] for x in combined]
        sorted_types = [x[1] for x in combined]

        # 计算前缀时间和剩余easy数量
        prefix = []
        total_time = 0
        for typ in sorted_types:
            total_time += a if typ == 0 else b
            prefix.append(total_time)

        max_points = 0

        # 情况1：解决所有问题
        if prefix[-1] <= T:
            return n

        # 情况2：在第一个问题强制前解决easy
        first_mandatory = sorted_times[0]
        if first_mandatory > 0:
            available = first_mandatory - 1
            max_easy = min(available // a, sum(1 for t in sorted_types if t == 0))
            max_points = max(max_points, max_easy)

        # 预处理剩余easy数量
        remaining_easy = [0] * (n + 1)
        count = 0
        for i in range(n-1, -1, -1):
            if sorted_types[i] == 0:
                count += 1
            remaining_easy[i] = count

        # 检查每个可能的分割点
        current_total_time = 0
        for i in range(n):
            current_total_time += a if sorted_types[i] == 0 else b
            if current_total_time > T:
                break

            # 计算后续可用时间
            next_mandatory = sorted_times[i+1] if i < n-1 else T + 1
            available_time = next_mandatory - current_total_time - 1
            if available_time < 0:
                continue

            # 计算可添加的easy数量
            possible = min(available_time // a, remaining_easy[i+1])
            max_points = max(max_points, i + 1 + possible)

        return max_points
