import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from math import sqrt
from math import isclose
import random
import re




class EacolourfulprospectInstructionGenerator(BaseInstructionGenerator):
    """Eacolourfulprospect Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Eacolourfulprospect指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = params.get('min_n', 1)
        self.max_n = params.get('max_n', 3)
        self.min_x = params.get('min_x', -10)
        self.max_x = params.get('max_x', 10)
        self.min_y = params.get('min_y', -10)
        self.max_y = params.get('max_y', 10)
        self.min_r = params.get('min_r', 1)
        self.max_r = params.get('max_r', 10)
    
    def case_generator(self):
        MAX_ATTEMPTS = 100
        for _ in range(MAX_ATTEMPTS):
            try:
                n = random.randint(self.min_n, self.max_n)
                circles = []
                for _ in range(n):
                    x = random.randint(self.min_x, self.max_x)
                    y = random.randint(self.min_y, self.max_y)
                    r = random.randint(self.min_r, self.max_r)
                    circles.append({'x': x, 'y': y, 'r': r})
                
                # Validate case constraints
                circles = [self.Circle(self.Vector(c['x'], c['y']), c['r']) for c in circles]
                m = 1
                for i in range(n):
                    for j in range(i+1, n):
                        if circles[i].O == circles[j].O and circles[i].r == circles[j].r:
                            raise ValueError("Duplicate circles")
                        m *= circles[i].fake(circles[j])
                        if m == 0:
                            raise ValueError("Invalid configuration")
                
                return {
                    'n': n,
                    'circles': [
                        {'x': c.O.x, 'y': c.O.y, 'r': c.r}
                        for c in circles
                    ]
                }
            except (ValueError, ZeroDivisionError):
                continue
        raise RuntimeError(f"Failed to generate valid case after {MAX_ATTEMPTS} attempts")
    
    @staticmethod
    def prompt_func(question_case):
        circles = question_case['circles']
        circles_str = "\n".join(f"{c['x']} {c['y']} {c['r']}" for c in circles)
        return (
            "Calculate regions formed by intersecting circles.\n"
            f"Input:\n{question_case['n']}\n{circles_str}\n"
            "Output format: [answer]INTEGER[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @classmethod
    def line_pt(cls, A, B):
        dir_vec = (A - B).rot()
        return cls.Line(dir_vec.x, dir_vec.y, dir_vec.x*A.x + dir_vec.y*A.y)

    @classmethod
    def _compute_regions(cls, identity):
        circles = [
            cls.Circle(
                cls.Vector(c['x'], c['y']),
                c['r']
            ) for c in identity['circles']
        ]
        n = identity['n']

        # Calculate intersection graph
        parent = list(range(n))
        def find(u):
            while parent[u] != u:
                parent[u] = parent[parent[u]]
                u = parent[u]
            return u
        def union(u, v):
            parent[find(u)] = find(v)

        vertices = set()
        edges = 0

        for i in range(n):
            for j in range(i+1, n):
                points = circles[i].intersect(circles[j])
                if points:
                    union(i, j)
                    edges += len(points)
                    vertices.update(points)

        components = len({find(i) for i in range(n)})
        return edges - len(vertices) + components + 1
