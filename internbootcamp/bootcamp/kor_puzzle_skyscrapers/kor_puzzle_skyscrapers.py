"""### 谜题描述
1.The game is played on an n*n grid, with skyscrapers placed in all cells on the grid.
2.Skyscrapers have a height of 1 to the size of the grid, i.e. 1 to 4 for a 4x4 puzzle.
3.You cannot have two skyscrapers of the same height in the same row or column.
4.The numbers on the sides of the boxes indicate how many skyscrapers you would see if you looked in the direction of the arrows, since taller buildings will be blocked by shorter ones.
5.Fill in the numbers in each cell to indicate the height of the skyscrapers.
6.The topic consists of an n*n matrix filled with X, with the numerical constraints mentioned above attached to the top and bottom.Example questions are as follows:

<example 0>
Grid Layout:
	1	2	3	2	
1	X	X	X	X	4
2	X	X	X	X	1
2	X	X	X	X	3
2	X	X	X	X	2
	3	2	1	2
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 0>

<example 1>
Grid Layout:
	2	1	2	3	
2	X	X	X	X	2
2	X	X	X	X	2
3	X	X	X	X	1
1	X	X	X	X	3
	1	3	2	2
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 1>

<example 2>
Grid Layout:
	2	3	2	1	
3	X	X	X	X	1
1	X	X	X	X	3
2	X	X	X	X	2
2	X	X	X	X	2
	2	2	1	3
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 2>

<example 3>
Grid Layout:
	2	4	2	1	
3	X	X	X	X	1
3	X	X	X	X	2
1	X	X	X	X	4
2	X	X	X	X	2
	2	2	1	3
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 3>

<example 4>
Grid Layout:
	1	2	2	2	
1	X	X	X	X	3
2	X	X	X	X	2
3	X	X	X	X	1
2	X	X	X	X	2
	4	1	3	2
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 4>

<example 5>
Grid Layout:
	2	1	2	3	
2	X	X	X	X	3
3	X	X	X	X	2
1	X	X	X	X	3
2	X	X	X	X	1
	2	3	2	1
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 5>

<example 6>
Grid Layout:
	2	3	5	2	1	
3	X	X	X	X	X	1
1	X	X	X	X	X	4
2	X	X	X	X	X	2
4	X	X	X	X	X	2
2	X	X	X	X	X	2
	2	3	1	2	3
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 6>

<example 7>
Grid Layout:
   2  4  3  1  2  
4  X  X  X  X  X  1
1  X  X  X  X  X  2
3  X  X  X  X  X  3
2  X  X  X  X  X  4
3  X  X  X  X  X  5
   3  2  2  2  1  
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 7>

<example 8>
Grid Layout:
	3	4	2	4	1	
3	X	X	X	X	X	1
2	X	X	X	X	X	2
1	X	X	X	X	X	3
3	X	X	X	X	X	2
2	X	X	X	X	X	2
	2	1	3	2	2
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 8>

<example 9>
Grid Layout:
	2	2	3	2	1	
2	X	X	X	X	X	1
4	X	X	X	X	X	2
2	X	X	X	X	X	2
1	X	X	X	X	X	5
2	X	X	X	X	X	3
	2	3	1	2	3
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
from bootcamp import Basebootcamp

class KorPuzzleSkyscrapersbootcamp(Basebootcamp):
    def __init__(self, **params):
        super().__init__(**params)
        self.n = params.get('n', 4)  # Default to 4x4 grid
    
    def case_generator(self):
        solution = self.generate_solution()
        left = [self.count_visible(row) for row in solution]
        right = [self.count_visible(reversed(row)) for row in solution]
        top = []
        bottom = []
        for col in range(self.n):
            column = [solution[row][col] for row in range(self.n)]
            top.append(self.count_visible(column))
            bottom.append(self.count_visible(reversed(column)))
        return {
            'n': self.n,
            'top': top,
            'bottom': bottom,
            'left': left,
            'right': right
        }
    
    def generate_solution(self):
        n = self.n
        # Generate base Latin square with shifted rows
        base = [[(i + j) % n + 1 for j in range(n)] for i in range(n)]
        random.shuffle(base)  # Shuffle rows
        
        # Shuffle columns
        cols = list(range(n))
        random.shuffle(cols)
        solution = []
        for row in base:
            new_row = [row[col] for col in cols]
            solution.append(new_row)
        
        # Additional row and column permutations for enhanced randomness
        for _ in range(n):
            i, j = random.sample(range(n), 2)
            solution[i], solution[j] = solution[j], solution[i]
        
        for _ in range(n):
            i, j = random.sample(range(n), 2)
            for row in solution:
                row[i], row[j] = row[j], row[i]
        
        return solution
    
    @staticmethod
    def count_visible(sequence):
        max_h, count = 0, 0
        for num in sequence:
            if num > max_h:
                count += 1
                max_h = num
        return count
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        grid_layout = "Grid Layout:\n"
        grid_layout += "\t" + "\t".join(map(str, question_case['top'])) + "\n"
        for i in range(n):
            left = question_case['left'][i]
            right = question_case['right'][i]
            x_part = "\t".join(['X'] * n)
            grid_layout += f"{left}\t{x_part}\t{right}\n"
        grid_layout += "\t" + "\t".join(map(str, question_case['bottom'])) + "\n"
        
        prompt = (
            "You are a city planner trying to arrange skyscrapers on an {n}x{n} grid. Each cell must contain a skyscraper with a height from 1 to {n}.\n"
            "The rules are:\n"
            "1. Each row and column must contain exactly one of each height (1-{n}).\n"
            "2. The numbers around the grid indicate how many skyscrapers are visible from that direction (taller buildings block shorter ones behind them).\n\n"
            "Given the following grid layout with visibility constraints:\n"
            "{grid_layout}\n"
            "Fill in the grid correctly. Format your answer as numbers arranged left to right, top to bottom, each row separated by a comma and space, enclosed in double square brackets.\n"
            "Example: [[1 2 3 4, 2 3 4 1, 3 4 1 2, 4 1 2 3]]\n"
        ).format(n=n, grid_layout=grid_layout)
        return prompt
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            # Handle multi-line formatting
            cleaned = ' '.join(last_match.splitlines()).replace(' , ', ', ').replace(', ', ',')
            rows = [r.strip() for r in cleaned.split(',')]
            solution = []
            for row in rows:
                solution.append([int(num) for num in row.split()])
            return solution
        except Exception as e:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        # Validate solution structure
        if not (isinstance(solution, list) and len(solution) == n and all(len(row) == n for row in solution)):
            return False
        
        # Verify Latin square properties
        expected = list(range(1, n+1))
        for row in solution:
            if sorted(row) != expected:
                return False
        for col in range(n):
            column = [solution[row][col] for row in range(n)]
            if sorted(column) != expected:
                return False
        
        # Verify visibility constraints
        for i in range(n):
            row = solution[i]
            if cls.count_visible(row) != identity['left'][i]:
                return False
            if cls.count_visible(reversed(row)) != identity['right'][i]:
                return False
        
        for j in range(n):
            column = [solution[i][j] for i in range(n)]
            if cls.count_visible(column) != identity['top'][j]:
                return False
            if cls.count_visible(reversed(column)) != identity['bottom'][j]:
                return False
        
        return True
