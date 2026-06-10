import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random
import math




class EoptimalpolygonperimeterInstructionGenerator(BaseInstructionGenerator):
    """Eoptimalpolygonperimeter Bootcamp指令生成器"""
    
    def __init__(self, max_n=6):
        """
        初始化Eoptimalpolygonperimeter指令生成器
        
        Args:
            max_n: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n
        random.seed(42)
    
    def case_generator(self):
        n = random.randint(3, self.max_n)
        while True:
            points = self.generate_convex_polygon(n)
            if points and len(points) == n:
                break
        
        # 计算vec
        vec = []
        for i in range(n):
            prev = (i-1) % n
            next_ = (i+1) % n
            dx_prev = points[i][0] - points[prev][0]
            dx_next = points[next_][0] - points[i][0]
            dy_prev = points[i][1] - points[prev][1]
            dy_next = points[next_][1] - points[i][1]
            
            sign = lambda x: -1 if x < 0 else 1 if x > 0 else 0
            if sign(dx_prev) != sign(dx_next) or sign(dy_prev) != sign(dy_next):
                vec.append(points[i])
        
        answers = [0]*(n+1)
        
        # 计算正确答案
        if len(vec) <= 3:
            perimeter = 0
            m = len(vec)
            for i in range(m):
                x1, y1 = vec[i]
                x2, y2 = vec[(i+1)%m]
                perimeter += abs(x1-x2) + abs(y1-y2)
            answers[3] = perimeter
            for k in range(4, n+1):
                answers[k] = perimeter
        else:
            # 计算k=4的情况
            perimeter = 0
            m = len(vec)
            for i in range(m):
                x1, y1 = vec[i]
                x2, y2 = vec[(i+1)%m]
                perimeter += abs(x1-x2) + abs(y1-y2)
            answers[4] = perimeter
            for k in range(5, n+1):
                answers[k] = perimeter
            
            # 正确计算k=3的情况（遍历所有原始点）
            max3 = 0
            for i in range(len(vec)):
                for j in range(i+1, len(vec)):
                    p1 = vec[i]
                    p2 = vec[j]
                    # 遍历所有原始点中的第三个点
                    for p3 in points:
                        if p3 == p1 or p3 == p2:
                            continue
                        min_x = min(p1[0], p2[0], p3[0])
                        max_x = max(p1[0], p2[0], p3[0])
                        min_y = min(p1[1], p2[1], p3[1])
                        max_y = max(p1[1], p2[1], p3[1])
                        candidate = 2 * (max_x - min_x + max_y - min_y)
                        if candidate > max3:
                            max3 = candidate
            answers[3] = max3
        
        return {
            "n": n,
            "points": points,
            "answers": answers[3:n+1]
        }
    
    @staticmethod
    def prompt_func(question_case):
        points = question_case["points"]
        n = question_case["n"]
        points_str = '\n'.join([f"{x} {y}" for x, y in points])
        return f"""Given a strictly convex polygon with {n} vertices in clockwise order:
{points_str}

Compute the maximum possible perimeter for each k from 3 to {n}. The polygon must be non-self-intersecting and use Manhattan distance.

Output format: Space-separated integers (k=3 to k={n}) within [answer] and [/answer].

Example format: [answer]12 14 16[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generate_convex_polygon(self, n):
        """生成严格凸多边形，确保无三点共线"""
        while True:
            # 生成随机点并计算凸包
            points = []
            for _ in range(n*2):  # 生成足够多的点以提高找到严格凸包的概率
                x = random.randint(-100, 100)
                y = random.randint(-100, 100)
                if (x, y) not in points:
                    points.append((x, y))

            # 计算凸包
            points = sorted(points)
            if len(points) < n:
                continue

            lower = []
            for p in points:
                while len(lower) >= 2 and self.cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)
            upper = []
            for p in reversed(points):
                while len(upper) >= 2 and self.cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)
            convex = lower[:-1] + upper[:-1]

            # 严格凸检查
            if len(convex) >= n and self.is_strictly_convex(convex):
                convex = convex[:n]
                # 顺时针排序
                center = (sum(x for x, y in convex)/n, sum(y for x, y in convex)/n)
                convex.sort(key=lambda p: (-math.atan2(p[1]-center[1], p[0]-center[0]), p))
                return convex

    def is_strictly_convex(self, points):
        """检查多边形是否严格凸"""
        n = len(points)
        for i in range(n):
            a, b, c = points[i], points[(i+1)%n], points[(i+2)%n]
            if self.cross(a, b, c) == 0:
                return False
        return True

    def cross(self, o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
