

### 谜题描述

Futoshiki is a logic puzzle played on an N×N grid where the objective is to fill each cell with a unique number from 1 to N, adhering to three core principles:

1. **Row and Column Uniqueness**:  
   Every row and column must contain all numbers from 1 to N exactly once, with no repetitions (similar to Sudoku).

2. **Inequality Constraints**:  
   Between certain pairs of adjacent cells (horizontally or vertically), there are inequality symbols (< or >). These symbols enforce relationships:  
   - **A > B** means the number in cell A must be greater than the number in cell B.  
   - **A < B** means the number in cell A must be less than the number in cell B.  
   The direction of the symbol determines the comparison (e.g., a \">\" between two horizontal cells means the left cell is greater; a \">\" between vertical cells means the upper cell is greater).

3. **Deductive Logic**:  
   The puzzle begins with some numbers pre-filled and inequalities provided. Solvers must deduce the remaining numbers by ensuring all uniqueness and inequality rules are satisfied simultaneously. Inequalities override potential number placements even if row/column uniqueness is temporarily met.

The challenge lies in balancing the constraints of uniqueness and inequalities to uniquely determine the solution.


请完成上述谜题的训练场环境类实现，包括所有必要的方法。
"""

from bootcamp import Basebootcamp
import random
import re
import ast
from typing import List, Dict, Any

class Futoshikibootcamp(Basebootcamp):
    def __init__(self, size=5, inequality_prob=0.3, retain_ratio=0.3):
        self.size = size
        self.inequality_prob = inequality_prob
        self.retain_ratio = retain_ratio

    def case_generator(self) -> dict:
        """生成带有唯一解的Futoshiki谜题实例"""
        solution = self._generate_latin_square()
        inequalities = self._generate_inequalities(solution)
        initial = self._generate_initial_grid(solution)
        return {
            'size': self.size,
            'initial': initial,
            'inequalities': inequalities
        }

    def _generate_latin_square(self) -> List[List[int]]:
        """生成随机拉丁方阵作为解"""
        n = self.size
        base_row = list(range(1, n+1))
        random.shuffle(base_row)
        rows = [base_row[i:] + base_row[:i] for i in range(n)]
        random.shuffle(rows)
        perm = list(range(1, n+1))
        random.shuffle(perm)
        return [[perm[x-1] for x in row] for row in rows]

    def _generate_inequalities(self, solution: List[List[int]]) -> List[Dict]:
        """根据解生成不等式约束"""
        inequalities = []
        for i in range(self.size):
            for j in range(self.size):
                if j+1 < self.size and random.random() < self.inequality_prob:
                    a, b = solution[i][j], solution[i][j+1]
                    inequalities.append({
                        'cell1': [i, j],
                        'cell2': [i, j+1],
                        'symbol': '>' if a > b else '<'
                    })
                if i+1 < self.size and random.random() < self.inequality_prob:
                    a, b = solution[i][j], solution[i+1][j]
                    inequalities.append({
                        'cell1': [i, j],
                        'cell2': [i+1, j],
                        'symbol': '>' if a > b else '<'
                    })
        return inequalities

    def _generate_initial_grid(self, solution: List[List[int]]) -> List[List[int]]:
        """生成初始谜题网格"""
        n = self.size
        indices = [(i, j) for i in range(n) for j in range(n)]
        retain_num = int(len(indices) * self.retain_ratio)
        selected = random.sample(indices, retain_num)
        grid = [[0]*n for _ in range(n)]
        for i, j in selected:
            grid[i][j] = solution[i][j]
        return grid

    @staticmethod
    def prompt_func(case) -> str:
        """生成面向用户的自然语言问题描述"""
        prompt = [
            "你是Futoshiki谜题专家，请根据以下条件解开谜题：",
            "\n规则说明：",
            "1. 填充1到N的整数（N为网格大小），满足：",
            "   - 每行和每列数字不重复",
            "   - 遵守所有不等式约束（>表示左边/上边数字更大）",
            f"\n初始网格（{case['size']}x{case['size']}，0表示空格）:"
        ]
        
        # 添加网格可视化
        for row in case['initial']:
            prompt.append("[" + " ".join(str(n) if n != 0 else "_" for n in row) + "]")
        
        # 添加不等式描述
        prompt.append("\n不等式约束：")
        for idx, ineq in enumerate(case['inequalities'], 1):
            c1, c2 = ineq['cell1'], ineq['cell2']
            direction = '右边' if c1[1]+1 == c2[1] else '下方'
            prompt.append(
                f"{idx}. 单元格({c1[0]}, {c1[1]}) {direction}的单元格应满足: "
                f"{ineq['symbol']}"
            )
        
        prompt.append(
            "\n将完整解答的二维数组放在[answer]标签内，例如：\n"
            "[answer]\n"
            "[[1,2,3],\n[2,3,1],\n[3,1,2]]\n"
            "[/answer]"
        )
        return "\n".join(prompt)

    @staticmethod
    def extract_output(output: str) -> List[List[int]]:
        """从模型输出中提取最后一个答案块"""
        answer_blocks = re.findall(
            r'\[answer\](.*?)\[/answer\]', 
            output, 
            re.DOTALL
        )
        if not answer_blocks:
            return None

        try:
            # 尝试解析最后一个答案块
            raw_answer = answer_blocks[-1].strip()
            return ast.literal_eval(raw_answer)
        except (SyntaxError, ValueError):
            return None

    @classmethod
    def _verify_correction(cls, solution: List[List[int]], case: dict) -> bool:
        """完整验证解的三个核心条件"""
        n = case['size']
        initial = case['initial']
        inequalities = case['inequalities']

        # 基础结构验证
        if len(solution) != n or any(len(row)!=n for row in solution):
            return False

        # 预填数字验证
        for i in range(n):
            for j in range(n):
                if initial[i][j] != 0 and solution[i][j] != initial[i][j]:
                    return False

        # 行列唯一性验证
        valid_numbers = set(range(1, n+1))
        for row in solution:
            if set(row) != valid_numbers:
                return False
        for col in zip(*solution):
            if set(col) != valid_numbers:
                return False

        # 不等式验证
        for ineq in inequalities:
            i1, j1 = ineq['cell1']
            i2, j2 = ineq['cell2']
            a, b = solution[i1][j1], solution[i2][j2]
            if not (a > b if ineq['symbol'] == '>' else a < b):
                return False

        return True
