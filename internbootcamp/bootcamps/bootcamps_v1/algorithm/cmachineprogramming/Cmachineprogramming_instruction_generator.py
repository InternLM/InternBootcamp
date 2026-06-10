import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CmachineprogrammingInstructionGenerator(BaseInstructionGenerator):
    """Cmachineprogramming Bootcamp指令生成器"""
    
    def __init__(self, max_n=8, max_k=3, time_max=20, **params):
        """
        初始化Cmachineprogramming指令生成器
        
        Args:
            max_n: 参数描述
            max_k: 参数描述
            time_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.max_n = max_n
        self.max_k = max_k
        self.time_max = time_max
    
    def case_generator(self):
        n = random.randint(3, self.max_n)
        k = random.randint(1, self.max_k)
        
        tasks = []
        for _ in range(n):
            si = random.randint(1, self.time_max)
            ti = random.randint(1, self.time_max//2)
            ci = random.randint(1, 100)
            tasks.append({
                'si': si,
                'ti': ti,
                'ci': ci
            })
        
        best_profit = self.calculate_optimal(tasks, k)
        
        return {
            'n': n,
            'k': k,
            'tasks': tasks,
            'optimal_profit': best_profit
        }
    
    @staticmethod
    def prompt_func(question_case):
        tasks = question_case['tasks']
        n = question_case['n']
        k = question_case['k']
        problem = f"Company X has {k} machine{'s' if k>1 else ''} and {n} tasks:\n"
        problem += "Each task has [start time, duration, profit]:\n"
        for i, t in enumerate(tasks, 1):
            problem += f"Task {i}: {t['si']} {t['ti']} {t['ci']}\n"
        problem += "\nSelect tasks to maximize profit without overlapping.\n"
        problem += "Output format: 0/1 sequence like: [answer]1 0 1[/answer]"
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def calculate_optimal(tasks, k):
        if not tasks:
            return 0

        sorted_tasks = sorted(tasks, key=lambda x: x['si'] + x['ti'])
        n = len(sorted_tasks)
        dp = [[0]*(k+1) for _ in range(n+1)]

        for i in range(1, n+1):
            current = sorted_tasks[i-1]
            s_i = current['si']
            end_i = s_i + current['ti']

            j = i-2
            while j >= 0 and (sorted_tasks[j]['si'] + sorted_tasks[j]['ti']) > s_i:
                j -= 1

            for m in range(1, k+1):
                include_profit = current['ci']
                if j >= 0:
                    include_profit += dp[j+1][m-1]
                dp[i][m] = max(dp[i-1][m], include_profit)

        return max(dp[n])

    @staticmethod
    def calculate_overlap(solution_tasks, k):
        timeline = []
        for task in solution_tasks:
            start = task['si']
            end = start + task['ti']
            timeline.append((start, 1))
            timeline.append((end, -1))

        timeline.sort()
        current = 0
        peak = 0
        for t, delta in timeline:
            current += delta
            peak = max(peak, current)
        return peak <= k
