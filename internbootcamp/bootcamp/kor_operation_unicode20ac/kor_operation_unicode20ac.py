"""### 谜题描述
A€B=2A+3B
A and B are matrices.Example questions are as follows:

<example 0>
A=
\[
\begin{pmatrix}
  1 & 2 \\
  3 & 4
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  5 & 6 \\
  7 & 8
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 0>

<example 1>
A=
\[
\begin{pmatrix}
  0 & 1 \\
  1 & 0
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  2 & 3 \\
  4 & 5
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 1>

<example 2>
A=
\[
\begin{pmatrix}
  -1 & -2 \\
  -3 & -4
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  1 & 2 \\
  3 & 4
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 2>

<example 3>
A=
\[
\begin{pmatrix}
  1 & 0 \\
  0 & 1
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  2 & 2 \\
  2 & 2
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 3>

<example 4>
A=
\[
\begin{pmatrix}
  2 & 4 \\
  6 & 8
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  1 & 3 \\
  5 & 7
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 4>

<example 5>
A=
\[
\begin{pmatrix}
  1 & 1 \\
  1 & 1
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  2 & 2 \\
  2 & 2
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 5>

<example 6>
A=
\[
\begin{pmatrix}
  3 & 3 \\
  3 & 3
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  4 & 4 \\
  4 & 4
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 6>

<example 7>
A=
\[
\begin{pmatrix}
  1 & 2 & 3\\
  4 & 5 & 6\\
  7 & 8 & 9
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  9 & 8 & 7\\
  6 & 5 & 4\\
  3 & 2 & 1
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b,c),(d,e,f),(g,h,i))]].
</example 7>

<example 8>
A=
\[
\begin{pmatrix}
  0 & 2 \\
  4 & 6
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  1 & 3 \\
  5 & 7
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 8>

<example 9>
A=
\[
\begin{pmatrix}
  1 & 2 \\
  3 & 4
\end{pmatrix}
\]
B=
\[
\begin{pmatrix}
  0 & 1 \\
  2 & 3
\end{pmatrix}
\]
Compute A€B.
The answer is a matrix, write it in this form:[[((a,b),(c,d))]].
</example 9>


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import math
import ast
from bootcamp import Basebootcamp

class KorOperationUnicode20acbootcamp(Basebootcamp):
    def __init__(self, matrix_shape=(2,2), min_val=-10, max_val=10):
        if not (len(matrix_shape) == 2 
                and all(isinstance(d, int) and d > 0 for d in matrix_shape)):
            raise ValueError("matrix_shape must be a tuple of two positive integers")
        if min_val > max_val:
            raise ValueError("min_val must be <= max_val")
        self.matrix_shape = matrix_shape
        self.min_val = min_val
        self.max_val = max_val
    
    def case_generator(self):
        rows, cols = self.matrix_shape
        return {
            'A': [[random.randint(self.min_val, self.max_val) for _ in range(cols)] 
                  for _ in range(rows)],
            'B': [[random.randint(self.min_val, self.max_val) for _ in range(cols)] 
                  for _ in range(rows)]
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        def matrix_to_latex(matrix):
            return '\\[\n\\begin{pmatrix}\n' + ' \\\\\n'.join(
                '  ' + ' & '.join(map(str, row)) for row in matrix
            ) + '\n\\end{pmatrix}\n\\]'
        
        rows = len(question_case['A'])
        cols = len(question_case['A'][0]) if rows else 0
        
        # 修正示例格式生成逻辑
        example_rows = [
            '(' + ','.join(['...']*cols) + ')' 
            for _ in range(rows)
        ]
        format_example = f'[[({",".join(example_rows)})]]'
        
        return f"""请计算矩阵运算A€B=2A+3B，其中：

矩阵A：
{matrix_to_latex(question_case['A'])}

矩阵B：
{matrix_to_latex(question_case['B'])}

答案应为{rows}x{cols}矩阵。按照格式要求将最终答案置于双括号内：
示例格式：{format_example}"""

    @staticmethod
    def extract_output(output):
        def safe_parse(s):
            try:
                parsed = ast.literal_eval(s)
                if not isinstance(parsed, tuple) or not all(isinstance(row, tuple) for row in parsed):
                    return None
                return parsed
            except:
                return None

        matches = re.findall(r'\[\[(.*?)\]\]', output, re.DOTALL)
        if not matches:
            return None
            
        clean_str = re.sub(r'\s+', '', matches[-1].strip())
        return safe_parse(clean_str)  # 移除破坏性字符处理

    @classmethod
    def _verify_correction(cls, solution, identity):
        A = identity['A']
        B = identity['B']
        
        try:
            # 维度校验
            if (len(solution) != len(A)) or any(len(s_row) != len(a_row) for s_row, a_row in zip(solution, A)):
                return False
            
            # 元素校验
            for i_row, (a_row, b_row) in enumerate(zip(A, B)):
                for j_col, (a, b) in enumerate(zip(a_row, b_row)):
                    expected = 2 * a + 3 * b
                    actual = solution[i_row][j_col]
                    if not math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-9):
                        return False
            return True
        except (TypeError, IndexError):
            return False
