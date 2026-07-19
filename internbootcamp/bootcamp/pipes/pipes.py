"""
### 谜题描述

The \"Pipes\" puzzle is a grid-based logic game where players connect colored endpoints with continuous, non-overlapping paths under the following rules:

1. **Grid Structure**: The puzzle is played on a rectangular grid. Each cell can either be empty, contain a pipe segment, or hold a colored endpoint.

2. **Endpoints**: 
   - Each color appears exactly twice on the grid, acting as an input (start) and output (end). 
   - All endpoints are pre-placed, and the goal is to connect matching colors.

3. **Pipe Path Rules**:
   - Paths must connect pairs of the same color, filling all cells between them.
   - Pipes can only run horizontally or vertically (no diagonal moves).
   - Paths must be continuous and cannot branch, cross other paths, or overlap. Each cell belongs to at most one pipe.

4. **Grid Completion**:
   - Every cell in the grid must be occupied by either a pipe segment or an endpoint. No empty cells are allowed in the solved state.

5. **Validity**:
   - A valid solution ensures all colored pairs are connected, and the entire grid is filled without rule violations.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import json
import re
from typing import Dict, List, Tuple

class Pipesbootcamp(Basebootcamp):
    def __init__(self, rows=5, cols=5, num_colors=2):
        self.rows = rows
        self.cols = cols
        self.num_colors = num_colors
        self.colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange'][:num_colors]

    def case_generator(self) -> dict:
        col_split = []
        base_cols = self.cols // self.num_colors
        remainder = self.cols % self.num_colors
        current = 0
        for i in range(self.num_colors):
            add = 1 if i < remainder else 0
            col_width = base_cols + add
            col_split.append((current, current + col_width))
            current += col_width

        endpoints = {}
        solution_paths = {}
        for i in range(self.num_colors):
            color = self.colors[i]
            start_col, end_col = col_split[i]
            path = []
            for row in range(self.rows):
                if row % 2 == 0:
                    cols_in_row = range(start_col, end_col)
                else:
                    cols_in_row = range(end_col-1, start_col-1, -1)
                for col in cols_in_row:
                    path.append((row, col))
            start = path[0]
            end = path[-1]
            endpoints[color] = [list(start), list(end)]
            solution_paths[color] = [list(coord) for coord in path]

        return {
            'grid_size': [self.rows, self.cols],
            'endpoints': endpoints,
            'solution_paths': solution_paths
        }

    @staticmethod
    def prompt_func(question_case) -> str:
        grid_size = question_case['grid_size']
        endpoints = question_case['endpoints']
        prompt = (
            f"You are playing a 'Pipes' puzzle on a {grid_size[0]}x{grid_size[1]} grid. Connect each pair of colored endpoints "
            "with continuous, non-overlapping paths that fill all cells. Follow these rules:\n"
            "1. Paths must be straight lines (horizontal/vertical)\n"
            "2. All cells must be filled\n"
            "3. Paths cannot cross or overlap\n\n"
            "Endpoints positions:\n"
        )
        for color, points in endpoints.items():
            prompt += f"- {color}: Start at {points[0]}, End at {points[1]}\n"
        prompt += (
            "\nFormat your answer as a JSON dictionary where keys are colors and values are coordinate lists "
            "from start to end. Enclose your answer within [answer] and [/answer] tags.\n"
            "Example:\n[answer]\n{\n  \"red\": [[0,0], [0,1], [1,1]],\n  \"blue\": [[2,2], [2,3]]\n}\n[/answer]"
        )
        return prompt

    @staticmethod
    def extract_output(output: str):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            solution = json.loads(matches[-1].strip())
            converted = {}
            for color, path in solution.items():
                converted_path = []
                for coord in path:
                    if isinstance(coord, list) and len(coord) == 2:
                        converted_path.append(tuple(coord))
                    else:
                        return None
                converted[color] = converted_path
            return converted
        except json.JSONDecodeError:
            return None

    @classmethod
    def _verify_correction(cls, solution: Dict[str, List[Tuple[int, int]]], identity: dict) -> bool:
        endpoints = {color: [tuple(ep) for ep in eps] for color, eps in identity['endpoints'].items()}
        grid_size = tuple(identity['grid_size'])
        all_coords = set()

        if set(solution.keys()) != set(endpoints.keys()):
            return False

        for color, path in solution.items():
            if len(path) < 2:
                return False
            start, end = path[0], path[-1]
            expected = set(endpoints[color])
            if {start, end} != set(expected):
                return False

            prev = path[0]
            for coord in path[1:]:
                dx, dy = abs(coord[0]-prev[0]), abs(coord[1]-prev[1])
                if dx + dy != 1:
                    return False
                prev = coord

            for coord in path:
                if coord in all_coords:
                    return False
                all_coords.add(coord)

        expected_coords = {(i, j) for i in range(grid_size[0]) for j in range(grid_size[1])}
        if all_coords != expected_coords:
            return False

        for color, path in solution.items():
            other_eps = set()
            for other_color in endpoints:
                if other_color != color:
                    other_eps.update(tuple(ep) for ep in endpoints[other_color])
            for coord in path[1:-1]:
                if coord in other_eps:
                    return False

        return True
