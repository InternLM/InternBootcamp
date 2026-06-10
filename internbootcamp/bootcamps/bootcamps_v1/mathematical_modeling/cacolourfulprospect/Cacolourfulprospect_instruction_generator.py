import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import re
import random




class CacolourfulprospectInstructionGenerator(BaseInstructionGenerator):
    """Cacolourfulprospect Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=3, x_range=(-10, 10), y_range=(-10, 10), r_range=(1, 10)):
        """
        初始化Cacolourfulprospect指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            x_range: 参数描述
            y_range: 参数描述
            r_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.x_range = x_range
        self.y_range = y_range
        self.r_range = r_range
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        circles = []
        for _ in range(n):
            while True:
                x = random.randint(*self.x_range)
                y = random.randint(*self.y_range)
                r = random.randint(*self.r_range)
                if not any((x, y, r) == c for c in circles):
                    circles.append((x, y, r))
                    break
        return {'n': n, 'circles': circles}
    
    @staticmethod
    def prompt_func(question_case):
        n = question_case['n']
        circles = question_case['circles']
        problem = (
            "在春节烟花表演中，计算圆形成的平面区域数。规则：\n"
            "1. 区域是连通的且面积大于0\n"
            "2. 每个区域由圆弧围成且无自交\n"
            "3. 恰好一个区域无限延伸\n\n"
            f"输入：\n{n}\n" + 
            "\n".join(f"{x} {y} {r}" for x, y, r in circles) +
            "\n答案格式：[answer]整数[/answer]"
        )
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def compute_regions(cls, n, circles):
        circles = [tuple(c) for c in circles]
        if n == 1:
            return 2
        if n == 2:
            return 2 + max(cls.ncut(*circles), 1)

        # 处理三个圆的情况
        c1, c2, c3 = circles
        cuts = (
            cls.ncut(c1, c2) 
            + cls.ncut(c2, c3) 
            + cls.ncut(c3, c1)
        )

        # 处理不相交圆对
        non_intersect_pairs = [
            (cls.ncut(c1, c2) == 0),
            (cls.ncut(c2, c3) == 0),
            (cls.ncut(c3, c1) == 0)
        ]
        if sum(non_intersect_pairs) >= 2:
            cuts += 1

        # 检测三圆公共交点
        if cuts >= 3 and cls.triple_intersection(circles):
            cuts -= 1
            if cls.collinear(c1[:2], c2[:2], c3[:2]):
                cuts -= 1

        return 2 + cuts

    @classmethod
    def ncut(cls, c1, c2):
        dx, dy = c1[0]-c2[0], c1[1]-c2[1]
        d_sq = dx**2 + dy**2
        r_sum = c1[2] + c2[2]
        r_diff = abs(c1[2] - c2[2])

        if d_sq > r_sum**2: return 0     # 外离
        if d_sq == r_sum**2: return 1    # 外切
        if d_sq < r_diff**2: return 0    # 内含
        if d_sq == r_diff**2: return 1   # 内切
        return 2                         # 相交

    @classmethod
    def triple_intersection(cls, circles):
        """精确检测三圆公共交点"""
        for i in range(3):
            a, b, c = circles[i], circles[(i+1)%3], circles[(i+2)%3]
            points = cls.get_intersections(a, b)
            for p in points:
                if cls.point_on_circle(p, c):
                    return True
        return False

    @staticmethod
    def get_intersections(c0, c1):
        """计算两圆精确交点"""
        x0, y0, r0 = c0
        x1, y1, r1 = c1

        d = math.hypot(x1-x0, y1-y0)
        if d > r0 + r1 or d < abs(r0 - r1):
            return []

        a = (r0**2 - r1**2 + d**2) / (2*d)
        h = math.sqrt(r0**2 - a**2)
        x2 = x0 + a*(x1 - x0)/d
        y2 = y0 + a*(y1 - y0)/d

        return [
            (x2 + h*(y1-y0)/d, y2 - h*(x1-x0)/d),
            (x2 - h*(y1-y0)/d, y2 + h*(x1-x0)/d)
        ] if h != 0 else [(x2, y2)]

    @staticmethod
    def point_on_circle(point, circle, eps=1e-8):
        """精确到1e-8的浮点误差判断"""
        x, y = point
        cx, cy, r = circle
        return abs((x - cx)**2 + (y - cy)**2 - r**2) < eps

    @staticmethod
    def collinear(p1, p2, p3):
        """三点共线检测优化版"""
        area = (p2[0] - p1[0])*(p3[1] - p1[1]) - (p2[1] - p1[1])*(p3[0] - p1[0])
        return abs(area) < 1e-8  # 允许浮点误差
