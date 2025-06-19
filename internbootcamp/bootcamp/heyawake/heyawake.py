

### 谜题描述

**Heyawake Puzzle Rules Explained:**

1. **Grid Structure**: 
   - Played on a rectangular grid divided into polyomino regions (\"rooms\"). 
   - Some rooms contain a number; others are unnumbered.

2. **Black Cell Placement**:
   - **Isolation**: No two black cells may be adjacent horizontally or vertically (diagonal is allowed).
   - **Room Constraints**: 
     - A room with a number **N** must contain exactly **N** black cells.
     - Unnumbered rooms can have any number of black cells (including zero).

3. **White Cell Connectivity**:
   - All white (uncolored) cells must form **a single contiguous area** connected edge-to-edge (diagonals do not count).

4. **Stripe Prevention (Three Rooms Rule)**:
   - In any row or column, a straight line of white cells cannot span **three or more rooms** without interruption by at least one black cell. This prevents white \"stripes\" crossing multiple rooms.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
from collections import deque

class Heyawakebootcamp(Basebootcamp):
    def __init__(self, rows=3, cols=3):
        self.rows = rows
        self.cols = cols
    
    def case_generator(self):
        # 生成一个简单的谜题实例，房间0的number为0，确保有解
        rows = self.rows
        cols = self.cols
        rooms = [
            {
                'cells': [(0, 0)],
                'number': 0
            },
            {
                'cells': [(i, j) for i in range(rows) for j in range(cols) if (i, j) != (0, 0)]
                # 无number
            }
        ]
        return {
            'rows': rows,
            'cols': cols,
            'rooms': rooms
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        rows = question_case['rows']
        cols = question_case['cols']
        rooms = question_case['rooms']
        problem_desc = "请解决以下Heyawake谜题：\n\n"
        problem_desc += "谜题规则：\n"
        problem_desc += "1. 黑格不能水平或垂直相邻。\n"
        problem_desc += "2. 每个带有数字的房间必须包含恰好该数字的黑格。未带数字的房间可以有任何数量的黑格。\n"
        problem_desc += "3. 所有白格必须形成一个连通的区域。\n"
        problem_desc += "4. 同一行或列中的连续白格不能跨越三个或更多不同的房间。\n\n"
        problem_desc += f"网格尺寸：{rows}行×{cols}列。\n"
        problem_desc += "房间划分及其数字说明：\n"
        for idx, room in enumerate(rooms):
            cells = room['cells']
            number = room.get('number', None)
            cells_str = ', '.join(f'({r},{c})' for r, c in cells)
            problem_desc += f"- 房间{idx+1}包含单元格 {cells_str}"
            if number is not None:
                problem_desc += f"，必须恰好有 {number} 个黑格"
            problem_desc += "。\n"
        problem_desc += "\n将答案以二维数组（0为白格，1为黑格）放在[answer]标签内，例如：\n[answer]\n[[0, 0, 0],\n[0, 1, 0],\n[0, 0, 0]]\n[/answer]"
        return problem_desc
    
    @staticmethod
    def extract_output(output):
        pattern = r'\[answer\](.*?)\[/answer\]'
        matches = re.findall(pattern, output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            solution = eval(last_match)
            if isinstance(solution, list) and all(isinstance(row, list) for row in solution):
                return solution
            return None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        # 验证solution结构合法性
        rows = identity['rows']
        cols = identity['cols']
        rooms = identity['rooms']
        if (not isinstance(solution, list) or len(solution) != rows or
            any(not isinstance(row, list) or len(row) != cols for row in solution)):
            return False
        for row in solution:
            for cell in row:
                if cell not in (0, 1):
                    return False
        
        # 规则1：黑格不能相邻
        for i in range(rows):
            for j in range(cols):
                if solution[i][j] == 1:
                    if j+1 < cols and solution[i][j+1] == 1:
                        return False
                    if i+1 < rows and solution[i+1][j] == 1:
                        return False
        
        # 规则2：房间约束
        for room in rooms:
            cells = room['cells']
            if 'number' in room:
                required = room['number']
                actual = sum(solution[i][j] for (i, j) in cells)
                if actual != required:
                    return False
        
        # 规则3：白格连通性
        white = [(i, j) for i in range(rows) for j in range(cols) if solution[i][j] == 0]
        if not white:
            return False
        visited = set()
        queue = deque([white[0]])
        visited.add(white[0])
        directions = [(-1,0), (1,0), (0,-1), (0,1)]
        while queue:
            i, j = queue.popleft()
            for dx, dy in directions:
                ni, nj = i+dx, j+dy
                if 0 <= ni < rows and 0 <= nj < cols and solution[ni][nj] == 0:
                    if (ni, nj) not in visited:
                        visited.add((ni, nj))
                        queue.append((ni, nj))
        if len(visited) != len(white):
            return False
        
        # 规则4：条纹防止规则
        # 构建房间映射
        room_id = [[-1 for _ in range(cols)] for _ in range(rows)]
        for idx, room in enumerate(rooms):
            for i, j in room['cells']:
                room_id[i][j] = idx
        
        # 检查行
        for i in range(rows):
            current_rooms = []
            for j in range(cols):
                if solution[i][j] == 1:
                    if len(current_rooms) >= 3:
                        return False
                    current_rooms = []
                else:
                    rid = room_id[i][j]
                    if not current_rooms or rid != current_rooms[-1]:
                        current_rooms.append(rid)
                    if len(current_rooms) >= 3:
                        return False
            if len(current_rooms) >= 3:
                return False
        
        # 检查列
        for j in range(cols):
            current_rooms = []
            for i in range(rows):
                if solution[i][j] == 1:
                    if len(current_rooms) >= 3:
                        return False
                    current_rooms = []
                else:
                    rid = room_id[i][j]
                    if not current_rooms or rid != current_rooms[-1]:
                        current_rooms.append(rid)
                    if len(current_rooms) >= 3:
                        return False
            if len(current_rooms) >= 3:
                return False
        
        return True
