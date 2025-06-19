

### 谜题描述

**Thermometers Puzzle Rules (General Explanation):**

1. **Grid Structure**: The puzzle is played on a square grid (size can vary). Each cell may belong to one or more \"thermometers\" represented by connected paths starting at a bulb (●) and ending at a tip. Thermometers may overlap or intersect.

2. **Number Placement**: 
   - Fill the grid with numbers such that each row and column contains all integers from 1 to *N* (where *N* is the grid size), with no repetition (like a Latin square).
   - **Exception**: Some variants may omit row/column uniqueness, depending on the puzzle's design.

3. **Thermometer Constraint**:
   - For every thermometer, the numbers must **strictly increase** from the bulb to the tip. Each subsequent cell along the thermometer's path must be a larger number than the preceding cell.

4. **Clues**:
   - Pre-filled numbers (if provided) must remain unchanged and act as constraints for solving.

**Objective**: Fill the grid while satisfying all row/column uniqueness rules (if applicable) and ensuring all thermometer paths follow the strict increasing order.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import re
import random

class Thermometersbootcamp(Basebootcamp):
    def __init__(self, size=5, num_thermometers=3, enforce_latin=True, max_retries=100):
        self.size = size
        self.num_thermometers = num_thermometers
        self.enforce_latin = enforce_latin
        self.max_retries = max_retries

    def case_generator(self):
        if self.enforce_latin:
            solution = self._generate_latin_square(self.size)
        else:
            raise NotImplementedError("Non-Latin square puzzles are not supported yet.")

        thermometers = []
        for _ in range(self.num_thermometers):
            thermometer = None
            for _ in range(self.max_retries):
                start_row = random.randint(0, self.size-1)
                start_col = random.randint(0, self.size-1)
                path = self._generate_thermometer_path(solution, start_row, start_col)
                if path:
                    thermometer = {'bulb': path[0], 'path': path}
                    break
            if not thermometer:
                raise ValueError(f"Failed to generate thermometer after {self.max_retries} attempts")
            thermometers.append(thermometer)
        
        return {
            "size": self.size,
            "thermometers": thermometers,
            "enforce_latin": self.enforce_latin
        }

    @staticmethod
    def _generate_latin_square(size):
        latin = []
        for i in range(size):
            row = [(i + j) % size + 1 for j in range(size)]
            latin.append(row)
        random.shuffle(latin)
        return latin

    @staticmethod
    def _generate_thermometer_path(solution, start_row, start_col):
        path = [(start_row, start_col)]
        current_value = solution[start_row][start_col]
        size = len(solution)
        
        while True:
            last_row, last_col = path[-1]
            neighbors = []
            for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                nr, nc = last_row + dr, last_col + dc
                if 0 <= nr < size and 0 <= nc < size and (nr, nc) not in path:
                    next_value = solution[nr][nc]
                    if next_value > current_value:
                        neighbors.append((nr, nc, next_value))
            if not neighbors:
                break
            nr, nc, nv = random.choice(neighbors)
            path.append((nr, nc))
            current_value = nv
        
        return path if len(path) >= 2 else None

    @staticmethod
    def prompt_func(question_case) -> str:
        def format_coord(coord):
            r, c = coord
            return f"行{r+1}列{c+1}"
        
        size = question_case['size']
        thermometers = question_case['thermometers']
        enforce_latin = question_case['enforce_latin']
        
        rules = [
            f"1. 在{size}x{size}的网格中填入1到{size}的数字。",
            "2. 每个温度计的路径必须从灯泡(●)开始严格递增。",
            f"3. 每{'行和列必须包含不重复的1到{size}' if enforce_latin else '行和列允许重复但需满足温度计约束'}。"
        ]
        
        thermo_desc = []
        for i, thermo in enumerate(thermometers, 1):
            path = thermo['path']
            bulb = format_coord(thermo['bulb'])
            tip = format_coord(path[-1])
            path_str = " → ".join(format_coord(p) for p in path)
            thermo_desc.append(f"温度计{i}: 从{bulb}到{tip}, 路径: {path_str}")

        return (
            "解决以下温度计谜题：\n\n" +
            "\n".join(rules) + "\n\n" +
            "温度计列表：\n" + "\n".join(thermo_desc) + "\n\n" +
            "将答案按行排列，每行数字用空格分隔，置于[answer]和[/answer]之间。示例：\n" +
            "[answer]\n1 2 3\n2 3 1\n3 1 2\n[/answer]"
        )

    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[\/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        last_answer = answer_blocks[-1].strip()
        rows = [line.strip() for line in last_answer.split('\n') if line.strip()]
        try:
            grid = [list(map(int, row.split())) for row in rows]
            if all(len(row) == len(grid[0]) for row in grid) and len(grid) == len(grid[0]):
                return grid
        except ValueError:
            pass
        return None

    @classmethod
    def _verify_correction(cls, solution, identity):
        size = identity['size']
        enforce_latin = identity.get('enforce_latin', True)
        thermometers = identity['thermometers']

        if len(solution) != size or any(len(row) != size for row in solution):
            return False
        if any(not (1 <= num <= size) for row in solution for num in row):
            return False

        if enforce_latin:
            expected = list(range(1, size+1))
            for row in solution:
                if sorted(row) != expected:
                    return False
            for col in range(size):
                if sorted(row[col] for row in solution) != expected:
                    return False

        for thermo in thermometers:
            path = thermo['path']
            values = [solution[r][c] for (r, c) in path]
            if any(values[i] >= values[i+1] for i in range(len(values)-1)):
                return False

        return True
