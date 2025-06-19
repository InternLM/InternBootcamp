

### 谜题描述

Norinori is a grid-based logic puzzle where the goal is to partition the entire grid into non-overlapping **domino regions** (each covering exactly two orthogonally adjacent cells). The rules are as follows:

1. **Grid Division**: The grid must be fully divided into domino-sized regions (2x1 or 1x2 tiles). Every cell belongs to exactly one domino.

2. **Shaded Cell Pairing**: The puzzle starts with some cells pre-shaded. Each shaded cell must be part of a domino region that contains **exactly two shaded cells**. In other words, every shaded cell must form a domino with one (and only one) adjacent shaded cell.

3. **Unshaded Regions**: The remaining unshaded cells are also grouped into domino regions, which may be oriented horizontally or vertically.

4. **No Overlaps/Intersections**: No two domino regions may overlap, and all dominoes must stay within the grid boundaries.

In summary, the challenge lies in pairing shaded cells into dominoes while ensuring the entire grid is covered, with no conflicting or isolated regions.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import ast

class Norinoribootcamp(Basebootcamp):
    def __init__(self, rows=6, cols=6, num_shaded_dominoes=3):
        if rows % 2 != 0 or cols % 2 != 0:
            raise ValueError("rows and cols must be even numbers.")
        total_dominoes = (rows * cols) // 2
        if num_shaded_dominoes < 0 or num_shaded_dominoes > total_dominoes:
            raise ValueError(f"num_shaded_dominoes must be between 0 and {total_dominoes}.")
        self.rows = rows
        self.cols = cols
        self.num_shaded_dominoes = num_shaded_dominoes

    def case_generator(self):
        dominoes = self._generate_tiling()
        shaded_dominoes = random.sample(dominoes, self.num_shaded_dominoes)
        shaded_cells = []
        for domino in shaded_dominoes:
            shaded_cells.append(tuple(domino[0]))
            shaded_cells.append(tuple(domino[1]))
        return {
            'shaded_cells': shaded_cells,
            'rows': self.rows,
            'cols': self.cols
        }

    def _generate_tiling(self):
        dominoes = []
        for i in range(0, self.rows, 2):
            for j in range(0, self.cols, 2):
                if random.choice([True, False]):
                    dominoes.append(((i, j), (i, j + 1)))
                    dominoes.append(((i + 1, j), (i + 1, j + 1)))
                else:
                    dominoes.append(((i, j), (i + 1, j)))
                    dominoes.append(((i, j + 1), (i + 1, j + 1)))
        return dominoes

    @staticmethod
    def prompt_func(question_case):
        shaded = question_case['shaded_cells']
        rows = question_case['rows']
        cols = question_case['cols']
        shaded_str = ', '.join([f"({r},{c})" for r, c in shaded])
        return f"""你正在解决一个Norinori谜题。规则如下：

1. 将{rows}x{cols}网格划分为1x2或2x1的骨牌，覆盖所有单元格。
2. 所有预着色单元格必须成对组成骨牌。
3. 未着色单元格也需组成骨牌，且不包含任何着色单元格。

预着色单元格的坐标为：{shaded_str}

请输出骨牌划分方案，将答案放在[answer]和[/answer]之间。格式示例：
[answer]
[[(0,0),(0,1)], [(1,0),(1,1)], ...]
[/answer]"""

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, flags=re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_match)
            if not isinstance(solution, list):
                return None
            for domino in solution:
                if len(domino) != 2:
                    return None
                for cell in domino:
                    if not isinstance(cell, (list, tuple)) or len(cell) != 2:
                        return None
                    if not all(isinstance(c, int) for c in cell):
                        return None
            return solution
        except:
            return None

    @classmethod
    def _verify_correction(cls, solution, identity):
        shaded = set(map(tuple, identity['shaded_cells']))
        rows = identity['rows']
        cols = identity['cols']
        all_cells = set()

        # 验证骨牌结构有效性
        for domino in solution:
            if len(domino) != 2:
                return False
            c1, c2 = tuple(domino[0]), tuple(domino[1])
            # 检查坐标范围
            if not (0 <= c1[0] < rows and 0 <= c1[1] < cols):
                return False
            if not (0 <= c2[0] < rows and 0 <= c2[1] < cols):
                return False
            # 检查相邻性
            if abs(c1[0]-c2[0]) + abs(c1[1]-c2[1]) != 1:
                return False
            # 检查重复
            if c1 in all_cells or c2 in all_cells:
                return False
            all_cells.update({c1, c2})

        # 检查全覆盖
        if len(all_cells) != rows * cols:
            return False

        # 检查着色配对
        for cell in shaded:
            cell = tuple(cell)
            found = False
            for domino in solution:
                if cell in domino:
                    other = domino[0] if domino[1] == cell else domino[1]
                    if other not in shaded:
                        return False
                    found = True
                    break
            if not found:
                return False

        # 检查非着色骨牌
        for domino in solution:
            shade_count = sum(1 for c in domino if tuple(c) in shaded)
            if shade_count not in (0, 2):
                return False

        return True
