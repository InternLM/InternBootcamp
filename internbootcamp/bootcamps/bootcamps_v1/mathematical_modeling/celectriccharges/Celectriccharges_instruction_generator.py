import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CelectricchargesInstructionGenerator(BaseInstructionGenerator):
    """Celectriccharges Bootcamp指令生成器"""
    
    def __init__(self, min_points=1, max_points=10, x_range=(-100, 100), y_range=(-100, 100)):
        """
        初始化Celectriccharges指令生成器
        
        Args:
            min_points: 参数描述
            max_points: 参数描述
            x_range: 参数描述
            y_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_points = min_points
        self.max_points = max_points
        self.x_range = x_range
        self.y_range = y_range
    
    def case_generator(self):
        points = set()
        n = random.randint(self.min_points, self.max_points)
        while len(points) < n:
            x = random.randint(*self.x_range)
            y = random.randint(*self.y_range)
            points.add((x, y))
        # 按x升序排序，x相同按y升序
        sorted_points = sorted(points, key=lambda p: (p[0], p[1]))
        return {
            "n": n,
            "points": [list(p) for p in sorted_points]
        }
    
    @staticmethod
    def prompt_func(question_case):
        points = question_case["points"]
        points_str = "\n".join(f"{x} {y}" for x, y in points)
        return f"""Programmer Celectriccharges needs to place electrons or protons at {len(points)} distinct points. Electrons move to (x, 0), protons to (0, y). Find the square of the minimal possible diameter after movement.

Points:
{points_str}

Put your answer within [answer] and [/answer]. Example: [answer]42[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_min_diameter(points):
        # 转换为按x排序的列表，确保与case_generator中的排序一致
        points_sorted = sorted(points, key=lambda p: (p[0], p[1]))
        n = len(points_sorted)
        if n == 0:
            return 0
        if n == 1:
            return 0

        # 预处理前缀和后缀的y的min和max
        pre_min = [0] * n
        pre_max = [0] * n
        pre_min[0] = points_sorted[0][1]
        pre_max[0] = points_sorted[0][1]
        for i in range(1, n):
            pre_min[i] = min(pre_min[i-1], points_sorted[i][1])
            pre_max[i] = max(pre_max[i-1], points_sorted[i][1])

        suf_min = [0] * n
        suf_max = [0] * n
        suf_min[-1] = points_sorted[-1][1]
        suf_max[-1] = points_sorted[-1][1]
        for i in range(n-2, -1, -1):
            suf_min[i] = min(suf_min[i+1], points_sorted[i][1])
            suf_max[i] = max(suf_max[i+1], points_sorted[i][1])

        # 辅助函数计算最大平方距离
        def max_sq_distance(electrons, protons):
            max_sq = 0
            # 电子移动到 (x,0)
            e_points = [(x, 0) for x in electrons]
            # 质子移动到 (0,y)
            p_points = [(0, y) for y in protons]
            all_points = e_points + p_points
            for i in range(len(all_points)):
                for j in range(i, len(all_points)):
                    dx = all_points[i][0] - all_points[j][0]
                    dy = all_points[i][1] - all_points[j][1]
                    sq = dx*dx + dy*dy
                    if sq > max_sq:
                        max_sq = sq
            return max_sq

        # 穷举所有可能的电子和质子的选择组合
        min_sq = float('inf')
        # 优化：对每个点，可以选择电子或质子，但n较大时穷举不适用，但此处假设n较小
        from itertools import product
        for choices in product([0, 1], repeat=n):
            electrons_x = []
            protons_y = []
            for i in range(n):
                if choices[i] == 0:
                    electrons_x.append(points_sorted[i][0])
                else:
                    protons_y.append(points_sorted[i][1])
            current_sq = max_sq_distance(electrons_x, protons_y)
            if current_sq < min_sq:
                min_sq = current_sq
        return min_sq
