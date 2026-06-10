import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import math
import re
import random
from itertools import combinations




class CcaptainmarmotInstructionGenerator(BaseInstructionGenerator):
    """Ccaptainmarmot Bootcamp指令生成器"""
    
    def __init__(self, n_regiments=1, same_origin=True, max_rotation=3, solvable_ratio=0.5, **kwargs):
        """
        初始化Ccaptainmarmot指令生成器
        
        Args:
            n_regiments: 参数描述
            same_origin: 参数描述
            max_rotation: 参数描述
            solvable_ratio: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()
        self.n_regiments = n_regiments
        self.same_origin = same_origin
        self.max_rotation = max_rotation
        self.solvable_ratio = solvable_ratio  # Probability to generate solvable cases
    
    def case_generator(self):
        case_data = {'regiments': [], 'n': self.n_regiments}
        
        for _ in range(self.n_regiments):
            # Generate regiment with configurable solvability
            regiment = self._generate_regiment(random.random() < self.solvable_ratio)
            case_data['regiments'].append(regiment)
        
        return case_data
    
    @staticmethod
    def prompt_func(question_case):
        input_lines = [str(question_case['n'])]
        for regiment in question_case['regiments']:
            for mole in regiment:
                input_lines.append(f"{mole[0]} {mole[1]} {mole[2]} {mole[3]}")
        
        problem_desc = (
            "Captain Marmot needs to rotate moles to form squares. Each mole can rotate 0-3 times around its home.\n"
            f"Input has {question_case['n']} regiments. Each regiment has 4 moles with format:\n"
            "x y a b (current position and home coordinates)\n"
            "Output the minimal total rotations per regiment, or -1 if impossible.\n"
            "Example format for 2 regiments:\n"
            "[answer]3[/answer]\n[answer]-1[/answer]\n"
            "Current input:\n" + "\n".join(input_lines)
        )
        return problem_desc 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_regiment(self, solvable=True):
        """Generate a regiment that can be solvable or unsolvable"""
        regiment = []
        origin_map = []

        # 1. Generate base points configuration
        if solvable:
            # Generate valid square points
            d = random.randint(1, 5)
            square_points = [
                (d, 0), (0, d), (-d, 0), (0, -d)
            ]
            random.shuffle(square_points)
        else:
            # Generate invalid points (non-square)
            square_points = [
                (random.randint(-5, 5), random.randint(-5, 5))
                for _ in range(4)
            ]
            # Ensure at least 3 points are collinear
            square_points[-1] = self._create_collinear_point(square_points[:3])

        # 2. Generate origins for each mole
        if self.same_origin:
            common_origin = (random.randint(-10, 10), random.randint(-10, 10))
            origin_map = [common_origin]*4
        else:
            origin_map = [(random.randint(-10, 10), random.randint(-10, 10)) 
                         for _ in range(4)]

        # 3. Apply rotations and build moles
        for idx in range(4):
            x_base, y_base = square_points[idx]
            a, b = origin_map[idx]

            # Apply random rotations
            rotations = random.randint(0, self.max_rotation)
            cx, cy = x_base, y_base
            for _ in range(rotations):
                nx = a - (cy - b)
                ny = b + (cx - a)
                cx, cy = nx, ny

            regiment.append((cx, cy, a, b))

        return regiment

    def _create_collinear_point(self, points):
        """Create a collinear point to make square impossible"""
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]

        # Find vector for points 0->1 and 0->2
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x3 - x1
        dy2 = y3 - y1

        # Ensure collinearity
        if dx1 * dy2 == dx2 * dy1:
            # Points are collinear, create another collinear point
            t = random.uniform(1.5, 3)
            return (x1 + t*dx1, y1 + t*dy1)
        else:
            # Force fourth point to be collinear
            t = random.uniform(0.5, 2)
            return (x2 + t*(x3 - x2), y2 + t*(y3 - y2))

    @staticmethod
    def _is_valid_square(points):
        # Calculate all pairwise squared distances
        dists = []
        for (x1, y1), (x2, y2) in combinations(points, 2):
            dist_sq = (x2-x1)**2 + (y2-y1)**2
            dists.append(dist_sq)

        # Verify square properties: 2 distinct distances (sides and diagonals)
        dists.sort()
        return (
            len(dists) == 6 and
            dists[0] == dists[1] == dists[2] == dists[3] and  # 4 equal sides
            dists[4] == dists[5] and                          # 2 equal diagonals
            dists[4] == 2 * dists[0] and                      # Diagonal = side*sqrt(2)
            dists[0] > 0                                      # Non-degenerate
        )

    @classmethod
    def _verify_single_regiment(cls, answer, regiment):
        """Verify single regiment answer"""
        rotation_states = []
        for mole in regiment:
            x, y, a, b = mole
            states = []
            current_x, current_y = x, y
            states.append((current_x, current_y))
            for _ in range(3):
                current_x, current_y = a - (current_y - b), b + (current_x - a)
                states.append((current_x, current_y))
            rotation_states.append(states)

        min_rotations = None
        for r0 in range(4):
            for r1 in range(4):
                for r2 in range(4):
                    for r3 in range(4):
                        points = [
                            rotation_states[0][r0],
                            rotation_states[1][r1],
                            rotation_states[2][r2],
                            rotation_states[3][r3]
                        ]
                        if cls._is_valid_square(points):
                            total = r0 + r1 + r2 + r3
                            if min_rotations is None or total < min_rotations:
                                min_rotations = total

        correct = min_rotations if min_rotations is not None else -1
        return answer == correct
