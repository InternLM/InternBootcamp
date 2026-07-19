"""### 谜题描述
1.The puzzles are played on a grid and the questions are given in the form of a matrix, consisting of X and 0.
2.The player needs to replace X for filling in d letters and 0 for separating words that cannot be filled in with letters.
3.Two lists of words are given, across and down. Across means fill in the words from left to right, and down means fill in the words from top to bottom.
4.During the game, many words will cross each other and share some letters.The letters that cross must match.
5.The question consists of a list of words and a matrix, where X denotes a grid to be filled with letters and 0 denotes a grid that does not need to be filled with letters,e.g.
X X X
0 X 0
0 X 0Example questions are as follows:

<example 0>
across:ACT
down:CAT
X        X        X
0        X        0
0        X        0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 0>

<example 1>
across: SAD SAVE
down: ADS VASE SAVED
X	X	X	X	0
X	0	X	0	X
X	0	X	X	X
X	0	X	0	X
X	0	0	0	0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 1>

<example 2>
across:WON
down:NOW OWN
X	0	0
X	X	X
X	0	X
0	0	X
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 2>

<example 3>
across:EAR
down:ARE ERA
X	0	0
X	0	X
X	X	X
0	0	X
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 3>

<example 4>
across:PAT
down:APT TAP
X	0	X
X	0	X
X	X	X
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 4>

<example 5>
across: RID RIP
down:DIP DRIP
0        0        0        0        X        0
X        X        X        0        X        0
0        0        X        X        X        0
0        0        X        0        0        0
0        0        X        0        0        0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 5>

<example 6>
across:FAR FAIR
down: AIR FIR
0        0        0        0        X        0
0        0        0        0        X        0
0        X        X        X        X        0
0        0        X        0        0        0
X        X        X        0        0        0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 6>

<example 7>
across:DEN TEN DENT
down: END NET TEND
0        0        X        0        0        X
X        X        X        0        0        X
X        0        X        X        X        X
X        0        0        0        0        0
X        X        X        0        0        0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 7>

<example 8>
across: ARK PAR
down: RAP PARK
X        0        X        0        0        0
X        0        X        X        X        0
X        X        X        0        0        0
0        0        X        0        0        0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 8>

<example 9>
aross: LAD LADY
down:DAY LAY
X	X	X	0	X	0
0	0	0	0	X	0
0	X	X	X	X	0
0	0	0	X	0	0
0	0	0	X	0	0
The answer should be given from left to right, top to bottom. Separate elements with a space and rows with a comma. Wrap the entire answer in double square brackets.
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
from bootcamp import Basebootcamp
import random
import string
import re

class KorPuzzleWordscapesbootcamp(Basebootcamp):
    def __init__(self, min_size=3, max_size=6):
        self.min_size = min_size
        self.max_size = max_size
    
    def case_generator(self):
        # 生成保证合法尺寸的网格
        rows = random.randint(max(3, self.min_size), self.max_size)
        cols = random.randint(max(3, self.min_size), self.max_size)
        
        def generate_valid_puzzle():
            while True:
                # 生成主横向单词
                main_word = random.choice(['CAT', 'DOG', 'CAR', 'BAT', 'ANT', 'OWL', 'BEE'])
                max_start_col = cols - len(main_word)
                if max_start_col < 0: continue
                start_col = random.randint(0, max_start_col)
                start_row = random.randint(0, rows-1)
                
                # 创建初始网格
                grid = [['0' for _ in range(cols)] for _ in range(rows)]
                for i in range(len(main_word)):
                    grid[start_row][start_col+i] = 'X'
                
                # 计算纵向单词的可行长度
                cross_pos = random.randint(0, len(main_word)-1)
                max_down_length = min(
                    start_row + 1,  # 向上可扩展空间
                    rows - start_row  # 向下可扩展空间
                )
                if max_down_length < 2: continue
                
                # 生成纵向单词（确保包含交叉字母）
                vertical_word = main_word[cross_pos] + ''.join(
                    random.choice(string.ascii_uppercase) 
                    for _ in range(max_down_length-1)
                )
                
                # 检查纵向单词布局的合法性
                valid = True
                vertical_length = len(vertical_word)
                for i in range(vertical_length):
                    r = start_row - cross_pos + i
                    if r < 0 or r >= rows:
                        valid = False
                        break
                    if grid[r][start_col + cross_pos] == 'X' and i != cross_pos:
                        valid = False
                if not valid: continue
                
                # 更新网格布局
                for i in range(vertical_length):
                    r = start_row - cross_pos + i
                    grid[r][start_col + cross_pos] = 'X'
                
                return {
                    "grid": grid,
                    "across": [main_word],
                    "down": [vertical_word],
                    "__solution__": self._generate_solution(
                        grid, main_word, vertical_word, 
                        start_row, start_col, cross_pos
                    )
                }

        return generate_valid_puzzle()
    
    def _generate_solution(self, grid, across_word, down_word, start_row, start_col, cross_pos):
        solution = []
        for row in grid:
            solution.append(['0' if cell == '0' else '_' for cell in row])
        
        # 填充横向单词
        for i, c in enumerate(across_word):
            solution[start_row][start_col+i] = c
        
        # 填充纵向单词
        vertical_start_row = start_row - cross_pos
        for i, c in enumerate(down_word):
            r = vertical_start_row + i
            solution[r][start_col + cross_pos] = c
        
        return solution

    @staticmethod
    def prompt_func(question_case):
        grid = question_case["grid"]
        across = question_case["across"]
        down = question_case["down"]
        
        grid_str = '\n'.join(' '.join(row) for row in grid)
        return f"""Solve this crossword puzzle:
- Grid layout (X=fillable, 0=blocked):
{grid_str}

Word lists:
- Across: {', '.join(across)}
- Down: {', '.join(down)}

Format your answer as space-separated values per row, comma-separated rows enclosed in double square brackets.
Example: [[A B 0, 0 C D]]"""

    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            last_match = matches[-1].strip()
            return [row.strip().split() for row in last_match.split(',')]
        except:
            return None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            expected = identity["__solution__"]
            return solution == expected
        except:
            return False
