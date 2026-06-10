import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def cw(a, b, c):
    return (b[0] - a[0]) * (c[1] - b[1]) - (c[0] - b[0]) * (b[1] - a[1]) < 0

def compute_expected(transformed_points):
    if not transformed_points:
        return 0
    transformed_points.sort()
    n = len(transformed_points)
    hull = [transformed_points[0]]
    for i in range(1, n):
        current_point = transformed_points[i]
        if cw(transformed_points[0], current_point, transformed_points[-1]) or (i == n - 1):
            while len(hull) >= 2 and not cw(hull[-2], hull[-1], current_point):
                hull.pop()
            hull.append(current_point)
    res = 0
    for i in range(1, len(hull)):
        if hull[i][0] != hull[i-1][0]:
            res += 1
    return res


class Fu2InstructionGenerator(BaseInstructionGenerator):
    """Fu2 Bootcamp指令生成器"""
    
    def __init__(self, max_n=10, max_x=1000):
        """
        初始化Fu2指令生成器
        
        Args:
            max_n: 参数描述
            max_x: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        self.max_x = max_x
    
    def case_generator(self):
        while True:
            n = random.randint(1, self.max_n)
            points = set()
            tried = 0
            max_attempts = 1000
            valid = True
            
            while len(points) < n and tried < max_attempts:
                tried += 1
                x = random.randint(-self.max_x, self.max_x)
                x_sq = x * x
                y_min = -10**6 - x_sq
                y_max = 10**6 - x_sq
                if y_min > y_max:
                    valid = False
                    break
                y_ = random.randint(y_min, y_max)
                points.add((x, y_ + x_sq))  # Store original (x, y)
            
            if not valid or len(points) < n:
                continue

            # Convert to transformed points for convex hull calculation
            transformed = [(x, y - x**2) for (x, y) in points]
            expected = compute_expected(transformed)
            
            case = {
                "n": n,
                "points": [[x, y] for (x, y) in points],
                "expected": expected
            }
            return case
    
    @staticmethod
    def prompt_func(question_case):
        points = question_case['points']
        points_str = '\n'.join([f"{x} {y}" for x, y in points])
        prompt = f"""Given {question_case['n']} distinct points, determine how many U-shaped parabolas (y=x²+bx+c) through at least two points have no other points strictly above them.

Input Format:
n
x₁ y₁
...
xₙ yₙ

Current Input:
{question_case['n']}
{points_str}

Output the count as [answer]integer[/answer]. Example: [answer]3[/answer]"""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

