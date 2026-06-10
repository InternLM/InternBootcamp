import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局变量 ===

MOD = 1000003


class CplumberInstructionGenerator(BaseInstructionGenerator):
    """Cplumber Bootcamp指令生成器"""
    
    def __init__(self, max_n=5, max_m=5, empty_prob=0.5):
        """
        初始化Cplumber指令生成器
        
        Args:
            max_n: 参数描述
            max_m: 参数描述
            empty_prob: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_n = max_n  
        self.max_m = max_m  
        self.empty_prob = empty_prob  
    
    def case_generator(self):
        n = random.randint(1, self.max_n)
        m = random.randint(1, self.max_m)
        if n * m > 5 * 10**5:  
            n, m = 1, 1  
        grid = []
        for _ in range(n):
            row = []
            for _ in range(m):
                if random.random() < self.empty_prob:
                    row.append('.')
                else:
                    row.append(random.choice(['1', '2', '3', '4']))
            grid.append(''.join(row))
        expected = self.solve_puzzle(n, m, grid)
        return {
            'n': n,
            'm': m,
            'grid': grid,
            'expected': expected
        }
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        m = question_case['m']
        grid = question_case['grid']
        grid_str = '\n'.join(grid)
        prompt = f"""Little John wants to become a plumber and has drawn a grid of pipes. Your task is to determine the number of possible non-leaking pipe configurations after filling all empty cells (marked with '.'). The answer must be given modulo 1000003.

**Pipe Segment Types:**
- Type 1: Connects **Top** and **Left** 
- Type 2: Connects **Top** and **Right**
- Type 3: Connects **Bottom** and **Left**
- Type 4: Connects **Bottom** and **Right**

**Rules:**
A system is non-leaking if EVERY pipe end connects to another pipe's end or the grid border. Two configurations are different if they differ in any cell.

**Input Format:**
- First line: n (rows) and m (columns)
- Next n lines: Grid rows with characters '1'-'4' or '.' 

**Current Grid (n={n}, m={m}):**
{grid_str}

**Output:**
The number of valid configurations modulo 1000003. Put your final answer within [answer] tags, e.g., [answer]1234[/answer]."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def solve_puzzle(n, m, grid):
        ans = 1
        # Row pattern checks
        for row in grid:
            valid_patterns = 0
            # Check two possible row patterns
            for start_with_12 in [False, True]:
                valid = True
                expect_12 = start_with_12
                for c in row:
                    if c == '.': 
                        expect_12 = not expect_12
                        continue
                    if expect_12:
                        if c not in {'1', '2'}:
                            valid = False
                            break
                    else:
                        if c not in {'3', '4'}:
                            valid = False
                            break
                    expect_12 = not expect_12
                if valid:
                    valid_patterns += 1
            ans = (ans * valid_patterns) % MOD

        # Column pattern checks
        for j in range(m):
            valid_patterns = 0
            for start_with_14 in [False, True]:
                valid = True
                expect_14 = start_with_14
                for i in range(n):
                    c = grid[i][j]
                    if c == '.':
                        expect_14 = not expect_14
                        continue
                    if expect_14:
                        if c not in {'1', '4'}:
                            valid = False
                            break
                    else:
                        if c not in {'2', '3'}:
                            valid = False
                            break
                    expect_14 = not expect_14
                if valid:
                    valid_patterns += 1
            ans = (ans * valid_patterns) % MOD
        return ans
