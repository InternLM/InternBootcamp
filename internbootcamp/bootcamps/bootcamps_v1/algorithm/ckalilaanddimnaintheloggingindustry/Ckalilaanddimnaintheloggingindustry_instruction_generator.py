import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from collections import deque
import random




class CkalilaanddimnaintheloggingindustryInstructionGenerator(BaseInstructionGenerator):
    """Ckalilaanddimnaintheloggingindustry Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Ckalilaanddimnaintheloggingindustry指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = params.get('n_min', 1)
        self.n_max = params.get('n_max', 10)
        self.a_step_min = params.get('a_step_min', 1)
        self.a_step_max = params.get('a_step_max', 100)
        self.b_step_min = params.get('b_step_min', 1)
        self.b_step_max = params.get('b_step_max', 100)
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        
        # Generate strictly increasing a
        a = [1]
        current = 1
        for _ in range(1, n):
            step = random.randint(self.a_step_min, self.a_step_max)
            current += step
            a.append(current)
        
        # Generate strictly decreasing b with bn=0
        b = [0]
        prev_b = 0
        for _ in range(n-1):
            step = random.randint(self.b_step_min, self.b_step_max)
            prev_b += step
            b.insert(0, prev_b)

        return {
            'n': n,
            'a': a,
            'b': b,
            'correct_answer': self._calculate_min_cost(n, a, b)
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        return f"""Kalila and Dimna need to cut down all trees with minimum cost. 

Input:
n = {question_case['n']}
a = {question_case['a']}
b = {question_case['b']}

Calculate the minimal total cost. Put your final answer within [answer]...[/answer].""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _calculate_min_cost(n, A, B):
        if n == 0:
            return 0
        dp = [0]*n
        lines = deque()
        lines.append((B[0], 0))  # (k, b)

        def get_x(line1, line2):
            k1, b1 = line1
            k2, b2 = line2
            if k1 == k2:
                return float('-inf')
            return (b2 - b1) / (k1 - k2)

        for i in range(1, n):
            # Remove outdated lines from end
            while len(lines) >= 2 and get_x(lines[-1], lines[-2]) <= A[i]:
                lines.pop()

            # Calculate current dp value
            best_k, best_b = lines[-1]
            dp[i] = best_b + best_k * A[i]

            # Maintain convex hull from front
            new_line = (B[i], dp[i])
            while len(lines) >= 2:
                x1 = get_x(lines[0], new_line)
                x2 = get_x(lines[0], lines[1])
                if x1 >= x2:
                    lines.popleft()
                else:
                    break
            lines.appendleft(new_line)

        return dp[-1]
