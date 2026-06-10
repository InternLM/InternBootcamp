import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import math
from itertools import permutations
from itertools import product
from itertools import combinations




class DrestorecubeInstructionGenerator(BaseInstructionGenerator):
    """Drestorecube Bootcamp指令生成器"""
    
    def __init__(self, solvable=True, cube_size=1, max_shift=3):
        """
        初始化Drestorecube指令生成器
        
        Args:
            solvable: 参数描述
            cube_size: 参数描述
            max_shift: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.solvable = solvable
        self.cube_size = cube_size
        self.max_shift = max_shift  # 控制立方体位置偏移范围
    
    def case_generator(self):
        if self.solvable:
            # 生成随机偏移的轴对齐立方体
            offset = [random.randint(-self.max_shift, self.max_shift) for _ in range(3)]
            base = [0, self.cube_size]
            original = []
            for x in base:
                for y in base:
                    for z in base:
                        pt = [x + offset[0], y + offset[1], z + offset[2]]
                        original.append(pt)
            
            # 随机打乱每个顶点的坐标顺序
            shuffled = []
            for pt in original:
                shuffled.append(random.choice(list(permutations(pt))))
            
            return {
                'input_points': [list(p) for p in shuffled],
                'solvable': True,
                'original_cube': original,
                'offset': offset
            }
        else:
            # 生成无法构成立方体的案例（保证坐标唯一但几何结构错误）
            points = []
            while len(points) < 8:
                pt = [random.randint(-2, 5) for _ in range(3)]
                if pt not in points:
                    points.append(pt)
                if len(points) == 7:  # 强制最后一个点破坏立方体结构
                    invalid = True
                    while invalid:
                        last_pt = [random.randint(-2, 5) for _ in range(3)]
                        if last_pt not in points:
                            points.append(last_pt)
                            invalid = not self._makes_invalid_cube(points)
            return {
                'input_points': points,
                'solvable': False
            }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        input_lines = [' '.join(map(str, p)) for p in question_case['input_points']]
        problem = "\n".join(input_lines)
        return (
            "Peter有一个各顶点坐标为整数的立方体，其弟Nick将每个顶点的三个数进行了排列交换。\n"
            "请判断能否恢复成立方体结构，若能，输出YES并按输入顺序给出正确坐标（每行为对应输入的排列），否则输出NO。\n"
            f"输入数据：\n{problem}\n"
            "答案要求：\n"
            "1. 第一行必须是YES或NO\n"
            "2. 如果YES，后续8行必须是对应输入的合法排列\n"
            "3. 坐标必须用空格分隔的三个整数\n"
            "请将最终答案放在[answer]和[/answer]标记之间，示例如下：\n"
            "[answer]\n"
            "YES\n"
            "0 0 0\n"
            "1 0 0\n"
            "...（其他6行）\n"
            "[/answer]"
        ) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _makes_invalid_cube(self, points):
        """确保points不能组成有效立方体"""
        # 快速初步检查
        if len(points) != 8:
            return True

        # 检查坐标唯一性
        if len(set(map(tuple, points))) < 8:
            return True

        # 计算所有距离的平方
        dists = []
        for (x1, y1, z1), (x2, y2, z2) in combinations(points, 2):
            dists.append((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)

        # 有效立方体应有3种不同距离值（边、面对角线、体对角线）
        unique_dists = set(dists)
        if len(unique_dists) != 3:
            return True

        # 检查各距离的数量是否符合立方体特征
        min_dist = min(unique_dists)
        edge_count = dists.count(min_dist)
        return edge_count != 12

    @classmethod
    def check_cube_possible(cls, input_points):
        """实际检查输入是否可能恢复成立方体（用于不可解案例的验证）"""
        # 尝试所有点的排列组合（优化版，仅用于验证生成案例）
        from itertools import permutations

        # 预处理所有可能的顶点排列
        candidates = []
        for pt in input_points:
            candidates.append(set(permutations(pt)))

        # 快速排除明显无效的情况
        unique_points = len(set(map(tuple, input_points)))
        if unique_points < 8:
            return False

        # 随机采样部分排列组合进行验证
        MAX_TRIES = 1000
        for _ in range(MAX_TRIES):
            test_case = [random.choice(list(c)) for c in candidates]
            if cls.is_cube(test_case):
                return True
        return False

    @staticmethod
    def is_cube(points):
        """优化后的几何验证逻辑"""
        # 计算所有点对的平方距离
        dist_counter = {}
        vectors = {}
        for i, j in combinations(range(8), 2):
            dx = points[i][0] - points[j][0]
            dy = points[i][1] - points[j][1]
            dz = points[i][2] - points[j][2]
            dist_sq = dx*dx + dy*dy + dz*dz
            dist_counter[dist_sq] = dist_counter.get(dist_sq, 0) + 1
            vectors[(i,j)] = (dx, dy, dz)

        # 有效立方体应有3种距离：边长（min）、面对角线、体对角线
        if len(dist_counter) != 3:
            return False

        # 检查各距离的数量关系
        edges = sorted(dist_counter.keys())
        a2, b2, c2 = edges  # a < b < c
        if dist_counter[a2] != 12 or dist_counter[b2] != 12 or dist_counter[c2] != 4:
            return False

        # 验证平方关系：b^2 = 2a^2，c^2 = 3a^2
        if not (math.isclose(b2, 2*a2, rel_tol=1e-9) and math.isclose(c2, 3*a2, rel_tol=1e-9)):
            return False

        # 验证向量正交性
        edge_vectors = [vec for (i,j), vec in vectors.items() if (points[i][0]-points[j][0])**2 + 
                       (points[i][1]-points[j][1])**2 + (points[i][2]-points[j][2])**2 == a2]

        # 每个边应有三个正交边
        for vec in edge_vectors[:3]:  # 检查前三个边即可
            orthogonal = 0
            for other in edge_vectors:
                if sum(a*b for a, b in zip(vec, other)) == 0:
                    orthogonal += 1
            if orthogonal < 3:
                return False

        return True
