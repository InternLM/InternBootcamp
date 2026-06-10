import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
from ast import literal_eval
from collections import deque




class GalaxiesInstructionGenerator(BaseInstructionGenerator):
    """Galaxies Bootcamp指令生成器"""
    
    def __init__(self, rows=5, cols=5):
        """
        初始化Galaxies指令生成器
        
        Args:
            rows: 参数描述
            cols: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        # Ensure odd dimensions for valid center placement
        self.rows = rows if rows % 2 != 0 else rows + 1
        self.cols = cols if cols % 2 != 0 else cols + 1
    
    def case_generator(self):
        """Generates a puzzle case with center(s) in a grid"""
        center = (self.rows // 2, self.cols // 2)
        return {
            'rows': self.rows,
            'cols': self.cols,
            'centers': [center]
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        """Generates problem description text with formatting instructions"""
        centers = question_case['centers']
        return f"""你是专业星系谜题解题专家，请根据以下信息划分星系：

**网格尺寸**: {question_case['rows']}x{question_case['cols']}
**中心位置**: {', '.join(f'({r},{c})' for r, c in centers)}

**规则要求**:
1. 每个星系必须包含且仅包含一个中心，且形状关于中心180度对称
2. 所有单元格必须属于且仅属于一个星系
3. 星系区域必须连通（上下左右相邻）

请按以下格式返回答案：
[answer]
[
    {{"center": (行坐标, 列坐标), "cells": [(坐标1), (坐标2), ...]}},
    ...
]
[/answer]

请确保：
1. 使用严格的Python列表和元组语法
2. 包含所有中心对应的星系
3. 每个坐标均为(row, column)格式""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _validate_structure(solution):
        """Validate basic solution structure"""
        if not isinstance(solution, list):
            return False
        for g in solution:
            if not isinstance(g, dict) or 'center' not in g or 'cells' not in g:
                return False
            if not isinstance(g['cells'], list) or len(g['cells']) == 0:
                return False
        return True

    @staticmethod
    def _check_centers(solution, expected_centers):
        """Verify all expected centers are present"""
        solution_centers = {tuple(g['center']) for g in solution}
        expected_set = {tuple(c) for c in expected_centers}
        return solution_centers == expected_set

    @staticmethod
    def _check_coverage(solution, rows, cols):
        """Verify complete grid coverage without overlaps"""
        all_cells = []
        for g in solution:
            all_cells.extend(map(tuple, g['cells']))
        expected = {(r, c) for r in range(rows) for c in range(cols)}
        return len(all_cells) == len(expected) and set(all_cells) == expected

    @classmethod
    def _validate_galaxy(cls, galaxy):
        """Validate individual galaxy constraints"""
        cells = [tuple(c) for c in galaxy['cells']]
        center = tuple(galaxy['center'])

        # Check center presence
        if center not in cells:
            return False

        # Check symmetry
        cx, cy = center
        for (x, y) in cells:
            sym = (2*cx - x, 2*cy - y)
            if sym not in cells:
                return False

        # Check connectivity
        return cls._is_connected(cells)

    @staticmethod
    def _is_connected(cells):
        """BFS check for region connectivity"""
        if not cells:
            return False

        visited = set()
        q = deque([cells[0]])
        visited.add(cells[0])

        while q:
            x, y = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = (x+dx, y+dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)

        return len(visited) == len(cells)
