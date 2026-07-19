"""### 谜题描述
1.A rectangular grid is given with a number at the end of each row and column indicating the sum of the weights of the filled black cells in that row or column.
2.In column i, the weight of the black grid is equal to its position in that column (i.e., 1 through n). Similarly, the weight of the black grid in row j is equal to its position in that row (i.e. 1 through n).
3.The player needs to blacken a number of cells in the grid such that the sum of the weights of the black cells in each row and column is equal to the given numbers.
4.The problem is given by a matrix in the form of a blank grid filled with X. Below and to the right of the matrix are attached the numerical constraints mentioned above. The player replaces the grid to be blacked out with 1.Example questions are as follows:

<example 0>
X  X  X  X  4
X  X  X  X  8
X  X  X  X  7
X  X  X  X  6
9  7  6  6  

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 0>

<example 1>
X  X  X  X  5
X  X  X  X  7
X  X  X  X  6
X  X  X  X  5
3  9  4  6  

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 1>

<example 2>
X  X  X  X  5
X  X  X  X  2
X  X  X  X  9
X  X  X  X  1
5  5  3  4      

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 2>

<example 3>
X  X  X  X  2
X  X  X  X  9
X  X  X  X  6
X  X  X  X  6
4  10  6  5  

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 3>

<example 4>
X  X  X  X  1
X  X  X  X  4
X  X  X  X  3
X  X  X  X  6
5  4  7  2

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 4>

<example 5>
X  X  X  X  X  5
X  X  X  X  X  1
X  X  X  X  X  5
X  X  X  X  X  5
X  X  X  X  X  4
2  1  1  5  7  

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 5>

<example 6>
X  X  X  X  X  13
X  X  X  X  X  3
X  X  X  X  X  14
X  X  X  X  X  13
X  X  X  X  X  12
5  3  15  13  13  

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 6>

<example 7>
X  X  X  X  X  X  16
X  X  X  X  X  X  12
X  X  X  X  X  X  16
X  X  X  X  X  X  15
X  X  X  X  X  X  18
X  X  X  X  X  X  10
15  19  14  13  17  11

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 7>

<example 8>
X  X  X  X  X  X  12
X  X  X  X  X  X  4
X  X  X  X  X  X  10
X  X  X  X  X  X  12
X  X  X  X  X  X  3
3  4  13  7  1  8

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 8>

<example 9>
X  X  X  X  X  X  5
X  X  X  X  X  X  17
X  X  X  X  X  X  9
X  X  X  X  X  X  13
X  X  X  X  X  X  9
X  X  X  X  X  X  8
14  10  12  4  13  10

The final answer should be given in order from left to right, top to bottom with each element separated by a space and different lines separated by \",\". Wrap your final answer in double square brackets, like this: [[your answer]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
from bootcamp import Basebootcamp
import random
import re

class KorPuzzleKukurasubootcamp(Basebootcamp):
    def __init__(self, min_size=4, max_size=7):
        self.min_size = min_size
        self.max_size = max_size

    def case_generator(self):
        """生成保证有解且具备可玩性的谜题"""
        while True:
            n = random.randint(self.min_size, self.max_size)
            grid = self._generate_valid_grid(n)
            
            row_sums = [sum(j+1 for j in range(n) if grid[i][j]) for i in range(n)]
            col_sums = [sum(i+1 for i in range(n) if grid[i][j]) for j in range(n)]
            
            # 确保至少每行/列有1个填充
            if 0 not in row_sums and 0 not in col_sums:
                return {
                    "row_sums": row_sums,
                    "col_sums": col_sums,
                    "size": n,
                    "solution": grid
                }

    def _generate_valid_grid(self, n):
        """生成有效初始解"""
        grid = []
        for _ in range(n):
            # 动态调整填充概率
            base_prob = 0.3 + random.random()*0.4  # 30%-70%
            grid.append([
                1 if random.random() < base_prob else 0 
                for _ in range(n)
            ])
        return grid

    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case["size"]
        row_str = "\n".join(
            " ".join(["X"]*n) + f" {s}" 
            for s in question_case["row_sums"]
        )
        col_str = " ".join(map(str, question_case["col_sums"]))
        
        return f"""你是一个数学谜题专家，需要解决以下网格填充问题：

网格规格：{n}x{n}正方形网格
数值说明：
- 每行右侧数字表示该行黑格子的列坐标之和（列号从左到右为1~{n}）
- 底部数字序列表示各列黑格子的行坐标之和（行号从上到下为1~{n}）

当前谜题：
{row_str}
{col_str}

答案要求：
1. 用0表示白格，1表示黑格
2. 各行数字用空格连接，行间用英文逗号分隔
3. 将最终答案包含在双中括号内

示例（4x4）：
[[1 0 0 0, 0 1 1 1, 1 0 1 0, 0 1 0 1]]"""

    @staticmethod 
    def extract_output(output):
        # 兼容中文括号和超长上下文
        pattern = r'\[{2}[^\[\]]*\]{2}'
        matches = re.findall(pattern, output)
        if not matches:
            return None
            
        last_match = matches[-1].strip('[]')
        # 统一处理中文标点
        processed = re.sub(r'[，]', ',', last_match)
        processed = re.sub(r'\s+', ' ', processed).strip()
        
        # 二次清洗
        rows = []
        for r in processed.split(','):
            clean_row = re.sub(r'[^\d\s]', '', r).strip()
            if clean_row:
                rows.append(clean_row)
                
        return ', '.join(rows) if rows else None

    @classmethod
    def _verify_correction(cls, solution, identity):
        try:
            n = identity["size"]
            # 格式验证
            if not re.fullmatch(r'([01] )+[01](, ([01] )+[01])*', solution):
                return False
                
            grid = []
            for row in solution.split(', '):
                elements = list(map(int, row.split()))
                if len(elements) != n:
                    return False
                grid.append(elements)
            
            # 数学验证
            row_valid = all(
                sum(j+1 for j in range(n) if grid[i][j]) == identity["row_sums"][i]
                for i in range(n)
            )
            col_valid = all(
                sum(i+1 for i in range(n) if grid[i][j]) == identity["col_sums"][j]
                for j in range(n)
            )
            
            return row_valid and col_valid
        except:
            return False
