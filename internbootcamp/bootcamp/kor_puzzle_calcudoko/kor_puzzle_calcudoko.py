"""### 谜题描述
1.The game is played on an NxN grid.
2.In each row and column, fill in the numbers from 1 to N. Each number can appear only once in each row and column.
3.The grid is divided into regions, each of which has a target number and an operator that indicates that the numbers in the region must equal the target number after a specified operation.
4.The numbers in each region cannot be repeated.
5.The question will give all the coordinates in the region and the requirements of the region, e.g., (1,1)(2,1)(3,1):12+ means that the sum of the numbers on the (first row, first column) (second row, first column) (third row, first column) is 12.Example questions are as follows:

<example 0>
The size of the grid is 4*4.
(1,1)(1,2)(1,3):6+
(1,4)(2,4):4*
(2,3)(3,3)(3,4):36*
(2,1)(3,1):2÷  
(4,3)(4,4):2÷ 
(2,2)(3,2):1-   
(4,1)(4,2):1-

Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 0>

<example 1>
The size of the grid is 4*4.
(1,1)(2,1):2÷  
(3,3)(3,4):2÷ 
(1,2)(1,3):1-
(1,4)(2,4):8*
(2,2)(2,3):3*
(3,1)(3,2)(4,1)(4,2):13+
(4,3)(4,4):2- 

Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 1>

<example 2>
The size of the grid is 4*4.
(1,1)(2,1):5+ 
(1,2)(1,3):5+
(2,2)(2,3):2÷  
(3,4)(4,4):2÷  
(1,4)(2,4):1-   
(4,1)(4,2):1-
(3,1)(3,2):12*
(3,3)(4,3):4*

Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 2>

<example 3>
The size of the grid is 4*4.
(1,1)(1,2):4*
(1,3)(1,4):1- 
(2,1)(3,1)(3,2):8+
(2,2)(2,3)(3,3)(4,3):12+
(2,4)(3,4)(4,4):8*
(4,1)(4,2):2÷

Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 3>

<example 4>
The size of the grid is 4*4.
(1,1)(1,2)(2,2):12*
(1,3)(1,4):5+  
(2,3)(2,4):5+
(2,1)(3,1):2÷
(3,2)(3,3)(4,3):8*
(4,1)(4,1):1-  
(3,4)(4,4):1- 

Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 4>

<example 5>
The size of the grid is 5*5.
(1,1)(2,1)(3,1):12+  
(3,4)(4,4)(5,4):12+
(1,2)(1,3)(2,2):8+
(1,4)(1,5):4*
(2,3)(2,4):6*
(2,5)(3,5):3-  
(3,2)(3,3):3-
(4,1)(4,2):5* 
(5,1)(5,2):1-
(4,3)(5,3):2÷
(4,5)(5,5):2- 
Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 5>

<example 6>
The size of the grid is 5*5.
(1,1)(2,1):5*
(1,2)(2,2)(2,3):10+
(1,3)(1,4):6+
(1,5)(2,5):6*
(2,4)(3,4):2- 
(3,2)(3,3):2-  
(4,3)(4,4):2-
(3,1)(4,1)(5,1):48*
(3,5)(4,5):3-
(4,2)(4,3):2÷
(4,4)(4,5):9+
Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 6>

<example 7>
The size of the grid is 5*5.
(1,1)(2,1):5*
(1,2)(2,2):7+
(1,3)(1,4):2÷  
(4,5)(5,5):2÷
(1,5)(2,5)(3,5): 60*
(2,3)(2,4)(3,3)(3,4): 6*
(3,1)(4,1):7+
(3,2)(4,2):5+
(5,1)(5,2):1-  
(4,3)(5,3):1-
(4,4)(5,4):2-

Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 7>

<example 8>
The size of the grid is 6*6.
(1,1)(2,1):6*
(1,2)(2,2):7+
(1,3)(2,3):12*
(1,4)(1,5)(1,6):20*
(2,4)(2,5):3÷ 
(5,5)(6,5):3÷
(2,6)(3,6):2÷ 
(5,1)(6,1):2÷
(3,1)(3,2)(4,1):11+
(3,3)($4,2)(4,3):2*
(3,4)(4,4):2- 
(5,2)(6,2):2- 
(5,3)(5,4):2-
(3,5)(4,5):3-
(6,3)(6,4):7+
(4,6)(5,6)(6,6):11+
Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 8>

<example 9>
The size of the grid is 6*6.
(1,1)(2,1):6+
(1,2)(1,3):3÷ (4,4)(5,4):3÷ (6,1)(6,2):3÷
(1,4)(1,5):8+ (4,6)(5,6):8+
(1,6)(2,6)(3,6):20*
(2,2)(2,3):2÷ (5,2)(5,3):2÷
(2,4)(2,5):5*
(3,1)(3,2):3- (3,3)(3,4):3-
(3,5)(4,5)(5,5):72*
(4,1)(5,1):4-
(4,2)(4,3):1-
(6,3)(6,4):5+
(6,5)(6,6):15*
Please provide each element in order from left to right, and from top to bottom, with each element separated by a space and each row separated by a comma. Ensure that your final answer is wrapped in double square brackets.

For example, if the answer is:
A B C
D E F
G H I

please output [[A B C,D E F,G H I]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from internbootcamp.bootcamp import Basebootcamp
import random
import re
from itertools import chain
from math import prod
from functools import reduce

class KorPuzzleCalcudokobootcamp(Basebootcamp):
    def __init__(self, grid_size=6):
        """
        初始化数独谜题训练场环境
        :param grid_size: 网格大小，默认为4x4
        """
        self.grid_size = grid_size
        super().__init__()

    def case_generator(self):
        """
        生成符合规则的谜题实例
        返回示例: {'size': 4, 'regions': [{'cells': [(1,1),(1,2)], 'operator': '+', 'target': 3}, ...]}
        """
        while True:
            # 生成数独解
            grid = self.generate_sudoku()
            if not grid:
                continue

            # 划分唯一数值区域
            regions = self.divide_into_regions(grid)
            if not regions:
                continue

            # 生成区域条件
            puzzle_data = self.generate_region_conditions(grid, regions)
            if puzzle_data:
                return puzzle_data

    def generate_sudoku(self):
        """生成符合数独规则的网格"""
        n = self.grid_size
        
        def backtrack(grid, row=0, col=0):
            if row == n: return True
            next_row = row + 1 if col == n-1 else row
            next_col = 0 if col == n-1 else col + 1

            if grid[row][col] != 0:
                return backtrack(grid, next_row, next_col)

            for num in random.sample(range(1, n+1), n):
                if self.is_valid_sudoku(grid, row, col, num):
                    grid[row][col] = num
                    if backtrack(grid, next_row, next_col):
                        return True
                    grid[row][col] = 0
            return False

        grid = [[0]*n for _ in range(n)]
        if backtrack(grid):
            return grid
        return None

    def is_valid_sudoku(self, grid, row, col, num):
        """验证数独有效性"""
        # 检查行
        if num in grid[row]:
            return False
        # 检查列
        for i in range(self.grid_size):
            if grid[i][col] == num:
                return False
        return True

    def divide_into_regions(self, grid):
        """划分唯一数值区域"""
        n = self.grid_size
        visited = [[False]*n for _ in range(n)]
        regions = []

        # 生成所有单元格坐标并随机排序
        cells = [(i, j) for i in range(n) for j in range(n)]
        random.shuffle(cells)

        for cell in cells:
            if visited[cell[0]][cell[1]]: continue

            region = []
            stack = [cell]
            visited[cell[0]][cell[1]] = True
            used_numbers = {grid[cell[0]][cell[1]]}

            while stack:
                current = stack.pop()
                region.append(current)

                # 获取未访问的相邻单元格
                neighbors = [
                    (current[0]+dx, current[1]+dy)
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]
                    if 0 <= current[0]+dx < n and 0 <= current[1]+dy < n
                    and not visited[current[0]+dx][current[1]+dy]
                ]
                random.shuffle(neighbors)

                for neighbor in neighbors:
                    val = grid[neighbor[0]][neighbor[1]]
                    if val not in used_numbers:
                        used_numbers.add(val)
                        visited[neighbor[0]][neighbor[1]] = True
                        stack.append(neighbor)
                        break  # 每次只扩展一个方向以确保区域连续性

            if len(region) >= 2:
                regions.append(region)
            else:
                # 无法形成有效区域，需要重新生成
                return None

        # 检查是否所有单元格都被分配
        if any(chain.from_iterable(visited)):
            return regions
        return None

    def generate_region_conditions(self, grid, regions):
        """生成区域运算条件"""
        conditions = []
        for region in regions:
            nums = [grid[i][j] for (i, j) in region]
            candidate_operators = []

            if len(nums) == 2:
                a, b = nums
                candidate_operators.append(('+', a + b))
                candidate_operators.append(('*', a * b))
                candidate_operators.append(('-', abs(a - b)))
                if max(a, b) % min(a, b) == 0:
                    candidate_operators.append(('÷', max(a, b) // min(a, b)))
            else:
                candidate_operators.append(('+', sum(nums)))
                candidate_operators.append(('*', reduce(lambda x,y:x*y, nums)))

            if not candidate_operators:
                return None

            op, target = random.choice(candidate_operators)
            conditions.append({
                'cells': [(i+1, j+1) for (i, j) in region],
                'operator': op,
                'target': target
            })

        return {'size': self.grid_size, 'regions': conditions}

    @staticmethod
    def prompt_func(question_case):
        """生成问题提示文本"""
        
        rule = "1.The game is played on an NxN grid.\n2.In each row and column, fill in the numbers from 1 to N. Each number can appear only once in each row and column.\n3.The grid is divided into regions, each of which has a target number and an operator that indicates that the numbers in the region must equal the target number after a specified operation.\n4.The numbers in each region cannot be repeated.\n5.The question will give all the coordinates in the region and the requirements of the region, e.g., (1,1)(2,1)(3,1):12+ means that the sum of the numbers on the (first row, first column) (second row, first column) (third row, first column) is 12.\n"
        
        size = question_case['size']
        regions = question_case['regions']
        prompt = [f"The size of the grid is {size}x{size}."]
        
        for region in regions:
            coords = ''.join(f"({r},{c})" for (r, c) in region['cells'])
            prompt.append(f"{coords}:{region['target']}{region['operator']}")
        
        prompt.append("\nPlease provide each element in order from left to right, and from top to bottom, "
                      "with each element separated by a space and each row separated by a comma. Ensure that your "
                      "final answer is wrapped in double square brackets.\n\nExample: "
                      "[[1 2 3,4 5 6,7 8 9]] for a 3x3 grid.")
        return rule + '\n'.join(prompt)

    @staticmethod
    def extract_output(output):
        """从模型输出中提取答案"""
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        
        try:
            content = matches[-1].replace('\n', '').strip()
            rows = [r.strip() for r in content.split(',') if r.strip()]
            return [list(map(int, row.split())) for row in rows]
        except:
            return None

    @classmethod
    def _verify_correction(cls, solution, identity):
        """验证答案正确性"""
        try:
            n = identity['size']
            # 验证基本尺寸
            if len(solution) != n or any(len(row) != n for row in solution):
                return False

            # 转换所有值为整数
            grid = []
            for row in solution:
                int_row = []
                for v in row:
                    int_row.append(int(v))
                grid.append(int_row)

            # 验证数独规则
            for i in range(n):
                if sorted(grid[i]) != list(range(1, n+1)):
                    return False
                if sorted(grid[j][i] for j in range(n)) != list(range(1, n+1)):
                    return False

            # 验证区域条件
            for region in identity['regions']:
                cells = region['cells']
                nums = [grid[r-1][c-1] for (r,c) in cells]
                
                # 检查唯一性
                if len(set(nums)) != len(nums):
                    return False
                
                # 检查运算
                op = region['operator']
                target = region['target']
                if op == '+':
                    if sum(nums) != target:
                        return False
                elif op == '*':
                    if reduce(lambda x,y: x*y, nums) != target:
                        return False
                elif op == '-':
                    if abs(nums[0]-nums[1]) != target:
                        return False
                elif op == '÷':
                    if max(nums)/min(nums) != target:
                        return False
                else:
                    return False

            return True
        
        except:
            return False

if __name__ == '__main__':
    while True:
        bootcamp_cls = KorPuzzleCalcudokobootcamp
        bootcamp = KorPuzzleCalcudokobootcamp()
        case = bootcamp.case_generator()
        while True:
            print('='*50, 'case', '='*50 + '\n', case, '\n' ,'='*50, 'case', '='*50)
            print('='*50, bootcamp_cls.__name__, '='*50 + '\n', bootcamp_cls.prompt_func(case),'\n' +'='*50, bootcamp_cls.__name__, '='*50)
            input_answer = input('Enter your answer: ')
            print('提取到的答案：', bootcamp_cls.extract_output(input_answer), '\n')
            print('你的答案得分：', bootcamp_cls.verify_score(input_answer, case,short_penalty=False, format_penalty=False))
            exit_or_not = input('是否退出？(y/n)')
            if exit_or_not == 'y':
                break