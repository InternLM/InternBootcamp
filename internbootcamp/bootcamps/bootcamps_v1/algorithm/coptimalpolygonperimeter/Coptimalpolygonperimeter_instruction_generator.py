import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import random




class CoptimalpolygonperimeterInstructionGenerator(BaseInstructionGenerator):
    """Coptimalpolygonperimeter Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Coptimalpolygonperimeter指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_points = params.get('min_points', 3)
        self.max_points = params.get('max_points', 10)
        self.coord_range = params.get('coord_range', (-100, 100))
        # Ensure min_points is at least 3
        self.min_points = max(3, self.min_points)
    
    def case_generator(self):
        # Generate n in specified range
        n = random.randint(self.min_points, self.max_points)
        
        # Generate bounding box with sufficient size
        minx = random.randint(self.coord_range[0], self.coord_range[1] - 10)
        maxx = minx + 10  # Ensure width is at least 10
        miny = random.randint(self.coord_range[0], self.coord_range[1] - 10)
        maxy = miny + 10  # Ensure height is at least 10
        
        # Generate points in strict convex polygon (simulating convex hull)
        points = []
        edges = ['bottom', 'right', 'top', 'left']
        edge_idx = 0
        
        # Generate points in clockwise order without colinear points
        for _ in range(n):
            edge = edges[edge_idx % 4]
            edge_idx += 1
        
            if edge == 'bottom':
                x = random.randint(minx, maxx - 1)  # Avoid rightmost point
                y = miny
            elif edge == 'right':
                x = maxx
                y = random.randint(miny + 1, maxy - 1)  # Avoid top/bottom extremes
            elif edge == 'top':
                x = random.randint(minx + 1, maxx)  # Avoid leftmost point
                y = maxy
            else:  # left
                x = minx
                y = random.randint(miny + 1, maxy - 1)
        
            points.append((x, y))
        
        # Calculate expected output using problem logic
        X = [p[0] for p in points]
        Y = [p[1] for p in points]
        maxx_val = max(X)
        minx_val = min(X)
        maxy_val = max(Y)
        miny_val = min(Y)
        
        ans_3 = 0
        for x, y in zip(X, Y):
            dx = max(maxx_val - x, x - minx_val)
            dy = max(maxy_val - y, y - miny_val)
            ans_3 = max(ans_3, dx + dy)
        ans_3 *= 2
        rec = 2 * ((maxx_val - minx_val) + (maxy_val - miny_val))
        
        # Generate expected output sequence
        expected_output = [ans_3] + [rec] * (n - 3)
        
        return {
            'n': n,
            'points': points,
            'expected_output': expected_output
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [str(question_case['n'])] + [
            f"{x} {y}" for x, y in question_case['points']
        ]
        input_example = '\n'.join(input_lines)
        
        return f"""\
Given a strictly convex polygon with {question_case['n']} vertices arranged clockwise. Compute maximum perimeter for k=3..n using Manhattan distances.

Input:
{input_example}

Output format: Space-separated integers f(3) to f(n).

Place your answer within [answer][/answer] tags. Example: [answer]12 14[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

