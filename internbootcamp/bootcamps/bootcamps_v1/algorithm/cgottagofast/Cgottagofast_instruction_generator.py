import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_expected_time(n, r, levels):
    a = levels
    left = 0.0
    right = 1e18
    answer = 0.0
    dp = [[0.0] * 5001 for _ in range(n + 2)]

    for _ in range(100):
        middle = (left + right) / 2
        for i in range(n + 1):
            for j in range(5001):
                dp[i][j] = 0.0

        for i in range(n - 1, -1, -1):
            for j in range(r + 1, 5001):
                dp[i + 1][j] = middle
            Fi, Si, Pi = a[i]
            p = Pi / 100.0
            q = (100 - Pi) / 100.0
            for j in range(r, -1, -1):
                fast = j + Fi
                slow = j + Si
                val_fast = Fi + (dp[i + 1][fast] if fast <= r else middle)
                val_slow = Si + (dp[i + 1][slow] if slow <= r else middle)
                expected = p * val_fast + q * val_slow
                dp[i][j] = min(middle, expected)
        if dp[0][0] < middle - 1e-12:
            answer = middle
            right = middle
        else:
            left = middle
    return answer


class CgottagofastInstructionGenerator(BaseInstructionGenerator):
    """Cgottagofast Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Cgottagofast指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_range = params.get('n_range', (1, 50))
        self.fi_range = params.get('fi_range', (1, 99))
        self.pi_range = params.get('pi_range', (80, 99))
        self.max_r = 5000
    
    def case_generator(self):
        N = random.randint(*self.n_range)
        levels = []
        sum_fi = 0
        for _ in range(N):
            Fi = random.randint(*self.fi_range)
            Si = random.randint(Fi + 1, 100)
            Pi = random.randint(*self.pi_range)
            levels.append((Fi, Si, Pi))
            sum_fi += Fi
        
        max_possible_r = min(sum_fi + 100 * N, self.max_r)
        R = random.randint(sum_fi, max_possible_r)
        
        return {
            'N': N,
            'R': R,
            'levels': [{'F': f, 'S': s, 'P': p} for (f, s, p) in levels]
        }
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['N']
        r = question_case['R']
        levels = question_case['levels']
        problem = (
            f"You are trying to set a speedrun record in a video game with {n} levels. Each level has two completion times: fast (Fi) and slow (Si > Fi). "
            "After each level, you can either continue or reset (restart from level 1). Your goal is to complete all levels within R seconds while minimizing the expected time spent.\n\n"
            "Input Details:\n"
            f"- Number of levels (N): {n}\n"
            f"- Time limit (R): {r} seconds\n"
            "Level Details (Fi = fast time, Si = slow time, Pi = probability of fast time in %):\n"
        )
        for i, lev in enumerate(levels, 1):
            problem += f"Level {i}: Fi={lev['F']}, Si={lev['S']}, Pi={lev['P']}%\n"
        problem += (
            "\nTask:\n"
            "Calculate the minimal expected time to achieve the goal. Provide your answer with at least 9 decimal places, enclosed in [answer] and [/answer] tags.\n"
            "Example: [answer]3.141592653[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

