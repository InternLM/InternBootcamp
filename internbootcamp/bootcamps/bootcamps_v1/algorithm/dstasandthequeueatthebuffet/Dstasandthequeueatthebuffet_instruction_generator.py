import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DstasandthequeueatthebuffetInstructionGenerator(BaseInstructionGenerator):
    """Dstasandthequeueatthebuffet Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10, a_max=1000):
        """
        初始化Dstasandthequeueatthebuffet指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            a_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n_min = n_min
        self.n_max = n_max
        self.a_max = a_max
    
    def case_generator(self):
        n = random.randint(self.n_min, self.n_max)
        # 生成delta并排序以确保正确顺序
        deltas = [random.randint(-50, 50) for _ in range(n)]
        deltas.sort()

        students = []
        for delta in deltas:
            # 确保a和b都≥1
            a_min = max(1, 1 - delta)
            a_max_val = min(a_min + 100, self.a_max)
            a = random.randint(a_min, a_max_val)
            b = a + delta
            students.append([a, b])
        
        # 关键修正：打乱学生顺序模拟真实输入
        random.shuffle(students)
        
        return {
            'n': n,
            'students': students
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        students = question_case['students']
        students_lines = '\n'.join(f"{s[0]} {s[1]}" for s in students)
        problem = f"""You are tasked with solving a queue rearrangement problem to minimize total dissatisfaction. 

**Problem Background:**
During a break at the buffet in the scientific lyceum of Kremland, a queue of {n} students formed. Each student has two characteristics: a_i and b_i. The dissatisfaction of a student placed in position j is calculated as a_i*(j-1) + b_i*(n-j), where (j-1) is the number of people to the left and (n-j) is the number to the right. Your task is to find the optimal arrangement to minimize the total dissatisfaction.

**Input Format:**
- The first line contains an integer n (1 ≤ n ≤ 10^5).
- The next n lines each contain two integers a_i and b_i (1 ≤ a_i, b_i ≤ 10^8).

**Current Problem Instance:**
{n}
{students_lines}

**Output Format:**
Output a single integer — the minimal total dissatisfaction possible after optimal rearrangement.

**Answer Instructions:**
Please place your final numerical answer within [answer] and [/answer] tags. For example: [answer]42[/answer]."""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

