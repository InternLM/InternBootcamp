

### 谜题描述

**Stitches Puzzle Rules**

1. **Objective**: Create a single continuous, non-intersecting loop by drawing horizontal/vertical \"stitches\" (line segments) between adjacent dots on a grid.

2. **Grid Structure**: 
   - Dots are arranged in a grid (e.g., square lattice).
   - Some dots contain numbers (0–3), indicating how many stitches must connect to them.

3. **Stitches**:
   - A stitch is a straight line between two orthogonally adjacent dots.
   - Stitches cannot cross, branch, or overlap.

4. **Key Rules**:
   - **Numbered Dots**: A dot with a number **N** must have exactly **N stitches** connected to it.
   - **Unnumbered Dots**: May have 0–2 stitches (default: 2 if part of the loop).
   - **Loop Requirement**: All stitches must form a single closed loop. Every dot in the loop must have exactly 2 stitches (entering/exiting), except numbered dots with values other than 2 (e.g., 0, 1, 3), which override this rule.

5. **Special Cases**:
   - **0**: The dot cannot be part of the loop (no stitches).
   - **1**: The dot is an endpoint (dead end), but this contradicts loop closure. Thus, **1s are typically invalid in classic loop rules** and may indicate edge-case mechanics (e.g., partial lines).
   - **3**: The dot acts as a \"branch,\" but this is prohibited in standard loop puzzles. Such clues may signal unique logic (e.g., overlapping regions or special constraints).

6. **Logic**:
   - Use numbers to deduce which dots must connect to others while ensuring the loop remains continuous and uncrossed.
   - Dots with **2** must lie on the loop; dots with **0** must be isolated.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
from collections import defaultdict

class Stitchesbootcamp(Basebootcamp):
    def __init__(self, rows=5, cols=5):
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        numbered_cells = []
        # Generate outer perimeter as solution
        perimeter_points = self._get_perimeter_points()
        # Add numbered cells: select some perimeter points as 2, some inner points as 0
        for x in range(self.rows):
            for y in range(self.cols):
                if (x, y) in perimeter_points:
                    if random.random() < 0.3:  # 30% chance to mark as 2
                        numbered_cells.append({'x': x, 'y': y, 'num': 2})
                else:
                    if random.random() < 0.1:  # 10% chance to mark inner as 0
                        numbered_cells.append({'x': x, 'y': y, 'num': 0})
        return {
            'rows': self.rows,
            'cols': self.cols,
            'numbered_cells': numbered_cells
        }
    
    def _get_perimeter_points(self):
        points = set()
        for x in [0, self.rows-1]:
            for y in range(self.cols):
                points.add((x, y))
        for y in [0, self.cols-1]:
            for x in range(1, self.rows-1):
                points.add((x, y))
        return points
    
    @staticmethod
    def prompt_func(question_case) -> str:
        rows = question_case['rows']
        cols = question_case['cols']
        cells = question_case['numbered_cells']
        cells_desc = '\n'.join([f"- 坐标 ({c['x']}, {c['y']}) 的数值为 {c['num']}" for c in cells])
        return f"""你是一个Stitches Puzzle解题专家，请根据以下规则解决谜题：

**规则说明**
1. 目标：在{rows}x{cols}的点阵中绘制水平/垂直缝线，形成**唯一闭合环**（无交叉、无分支）。
2. 数字规则：
   - 数字N表示该点必须连接N条缝线
   - 数值0必须无连接，数值2必须连接两条
3. 未标数字的点属于环时必须有2条缝线
4. 缝线必须形成连续闭合环，所有点至多属于一个环

**当前谜题**
数字点列表（坐标从0开始）：
{cells_desc if cells else "无数字点"}

**答案格式**
请将答案包含在[answer]和[/answer]之间，格式为：
[[(x1,y1),(x2,y2)], [(x3,y3),(x4,y4)], ...]
确保每个缝线为相邻点坐标，如示例所示。"""

    @staticmethod
    def extract_output(output):
        import re
        import ast
        # Find last answer block
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            solution = ast.literal_eval(last_answer)
            if not isinstance(solution, list):
                return None
            for stitch in solution:
                if len(stitch) != 2 or not all(isinstance(p, tuple) and len(p)==2 for p in stitch):
                    return None
            return solution
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            rows = identity['rows']
            cols = identity['cols']
            numbered_cells = {(c['x'], c['y']): c['num'] for c in identity['numbered_cells']}
            
            # 验证基本结构
            stitches = set()
            for stitch in solution:
                # 验证缝线格式
                if len(stitch) != 2:
                    return False
                p1, p2 = stitch
                if not (isinstance(p1, tuple) and isinstance(p2, tuple) and len(p1)==2 and len(p2)==2):
                    return False
                x1, y1 = p1
                x2, y2 = p2
                # 验证坐标有效性
                if not (0 <= x1 < rows and 0 <= y1 < cols and 0 <= x2 < rows and 0 <= y2 < cols):
                    return False
                # 验证相邻性
                dx = abs(x1 - x2)
                dy = abs(y1 - y2)
                if not ((dx == 1 and dy == 0) or (dy == 1 and dx == 0)):
                    return False
                # 标准化缝线存储
                stitches.add(frozenset({p1, p2}))
            
            # 构建邻接表
            graph = defaultdict(list)
            for s in stitches:
                p1, p2 = s
                graph[p1].append(p2)
                graph[p2].append(p1)
            
            # 检查数字点约束
            for (x, y), num in numbered_cells.items():
                actual = len(graph.get((x, y), []))
                if actual != num:
                    return False
            
            # 检查所有节点的度数
            visited = set()
            for node in graph:
                # 处理未访问节点
                if node in visited:
                    continue
                # 检查是否为合法环结构
                current = node
                prev = None
                path = []
                while True:
                    next_nodes = [n for n in graph[current] if n != prev]
                    if len(next_nodes) != 1:
                        break  # 分支或末端
                    prev, current = current, next_nodes[0]
                    if current == node:  # 闭环检查
                        break
                    path.append(current)
                    if current in visited:
                        return False
                    visited.add(current)
                # 验证是否形成闭环
                if current != node or len(graph[node]) != 2:
                    return False
            
            # 检查未编号点度数
            for node in graph:
                if node not in numbered_cells:
                    if len(graph[node]) not in (0, 2):
                        return False
            
            # 检查单一环
            # 确保所有连接点被访问且构成单个环
            component = []
            stack = []
            if graph:
                start = next(iter(graph))
                stack.append(start)
                visited_nodes = set()
                while stack:
                    node = stack.pop()
                    if node in visited_nodes:
                        continue
                    visited_nodes.add(node)
                    for neighbor in graph[node]:
                        if neighbor not in visited_nodes:
                            stack.append(neighbor)
                if len(visited_nodes) != len(graph):
                    return False
            return True
        except:
            return False
