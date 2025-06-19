

### 谜题描述

Dominosa is a logic puzzle where the goal is to partition a grid of numbers into non-overlapping dominoes (2x1 or 1x2 rectangles) following these rules:

1. **Grid Structure**: 
   - The grid has an even number of cells, arranged in rows and columns. The exact dimensions vary, but they must allow full coverage by dominoes (e.g., a 5x6 grid, 7x8 grid, etc.).

2. **Domino Formation**:
   - Each domino consists of two orthogonally adjacent cells (horizontal or vertical neighbors).
   - Every cell in the grid must belong to exactly one domino.

3. **Uniqueness Constraint**:
   - Each domino is defined by an unordered pair of numbers (e.g., a domino with numbers 3 and 5 is equivalent to one with 5 and 3).
   - Every domino in the solution must appear **exactly once**. If two dominoes share the same pair of numbers, the puzzle is invalid.

4. **Number Set**:
   - The numbers in the grid are derived from a contiguous set (e.g., 0 to N). The maximum number (N) determines the total number of possible unique domino pairs, which must match the grid size (e.g., for numbers 0-4, there are 15 unique domino pairs, requiring a 30-cell grid).

The challenge is to deduce the domino layout that satisfies all constraints without repetition. Logical elimination and pattern recognition are key to solving the puzzle.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import itertools
import random
import re

class Dominosabootcamp(Basebootcamp):
    def __init__(self, n=4):
        """
        初始化Dominosa训练场环境，配置数字范围和网格参数。
        
        参数:
            n: 数字范围上限，生成数字0-n的连续集合，默认4对应5x6网格
        """
        self.n = n
        self.rows = n + 1
        self.cols = n + 2

    def case_generator(self):
        """
        生成合法Dominosa谜题实例，保证至少存在一个解。
        
        返回:
            dict: 包含网格布局和参数的字典，结构为{'grid': 二维列表, 'n': 数字范围}
        """
        # 生成所有可能的无序数字对并打乱顺序
        pairs = list(itertools.combinations_with_replacement(range(self.n + 1), 2))
        random.shuffle(pairs)
        # 创建网格并填充数字对
        grid = []
        pair_index = 0
        if self.cols % 2 == 0:
            for i in range(self.rows):
                row = []
                for j in range(0, self.cols, 2):
                    a, b = pairs[pair_index]
                    row.extend([a, b])  # 水平排列数字对
                    pair_index += 1
                grid.append(row)
        else:
            grid = [[] for _ in range(self.rows)]
            for i in range(0, self.cols):
                for j in range(0, self.rows, 2):
                    a, b = pairs[pair_index]
                    grid[j].append(a)
                    grid[j+1].append(b)
                    pair_index += 1

        return {
            'grid': grid,
            'n': self.n
        }

    @staticmethod
    def prompt_func(question_case) -> str:
        """
        将数字网格转化为自然语言问题描述，包含格式说明。
        
        参数:
            question_case: case_generator生成的谜题实例
            
        返回:
            str: 包含网格布局和解答要求的提示文本
        """
        grid = question_case['grid']
        n = question_case['n']
        
        prompt = f"""你是Dominosa谜题专家，请将以下{len(grid)}x{len(grid[0])}网格划分为不重复的骨牌组合。每个骨牌必须覆盖两个相邻单元格（水平或垂直），且所有数字对唯一。

网格布局（行号从0开始）：
"""
        for i, row in enumerate(grid):
            prompt += f"行{i}:\t" + "\t".join(map(str, row)) + "\n"

        prompt += f"""
规则说明：
1. 数字范围：0-{n}，每个骨牌包含两个不同或相同的数字
2. 数对(a,b)与(b,a)视为相同，必须唯一
3. 必须完全覆盖所有单元格

答案格式要求：
将每个骨牌表示为两个坐标对，每行一个骨牌，如：
[answer]
(行号,列号),(行号,列号)
...[/answer]

请确保：
- 使用英文括号和逗号
- 按最后出现的答案块评分
- 坐标按行号、列号顺序"""
        return prompt

    @staticmethod
    def extract_output(output):
        """
        从模型输出中提取最后一个答案块并解析坐标。
        
        参数:
            output: 模型完整输出文本
            
        返回:
            list: 提取的骨牌坐标列表，格式[(坐标1, 坐标2), ...]
        """
        # 匹配最后一个答案块
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        dominoes = []
        last_block = answer_blocks[-1].strip()
        
        # 解析坐标对
        pattern = r'\((\d+)\s*,\s*(\d+)\)\s*,\s*\((\d+)\s*,\s*(\d+)\)'
        matches = re.findall(pattern, last_block)
        for m in matches:
            try:
                coord1 = (int(m[0]), int(m[1]))
                coord2 = (int(m[2]), int(m[3]))
                dominoes.append((coord1, coord2))
            except:
                continue
        
        return dominoes if dominoes else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        """
        验证答案的完整性和正确性。
        
        参数:
            solution: 提取的骨牌坐标列表
            identity: case_generator生成的谜题实例
            
        返回:
            bool: 是否满足所有谜题约束
        """
        if not solution:
            return False

        grid = identity['grid']
        rows = len(grid)
        cols = len(grid[0]) if rows > 0 else 0
        total_cells = rows * cols
        
        # 验证覆盖完整性
        covered = set()
        pairs = []
        
        for domino in solution:
            # 校验坐标数量
            if len(domino) != 2:
                return False
            (r1, c1), (r2, c2) = domino
            
            # 校验坐标有效性
            if not (0 <= r1 < rows and 0 <= c1 < cols):
                return False
            if not (0 <= r2 < rows and 0 <= c2 < cols):
                return False
            
            # 校验相邻性
            if not ((r1 == r2 and abs(c1 - c2) == 1) or 
                    (c1 == c2 and abs(r1 - r2) == 1)):
                return False
            
            # 检查重复覆盖
            if (r1, c1) in covered or (r2, c2) in covered:
                return False
            
            covered.update([(r1, c1), (r2, c2)])
            
            # 记录数字对
            a, b = grid[r1][c1], grid[r2][c2]
            pairs.append(tuple(sorted((a, b))))
        
        # 检查覆盖率
        if len(covered) != total_cells:
            return False
        
        # 检查唯一性
        return len(pairs) == len(set(pairs))
