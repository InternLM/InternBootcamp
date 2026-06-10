import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import re
import ast
import json
import sys
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.calcudoku.lib.calcudoku_generator import CalcudokuGenerator
import random




class CalcudokuInstructionGenerator(BaseInstructionGenerator):
    """Calcudoku Bootcamp指令生成器"""
    
    def __init__(self, size:int = 6,  group_size_range:tuple =(1,4)):
        """
        初始化Calcudoku指令生成器
        
        Args:
            size: 参数描述
            group_size_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__()   
        self.size = size
        self.group_size_range = group_size_range
    
    def case_generator(self):
        grid = self.generator(self.size, self.group_size_range)
        self.prompt = self.get_question()
        return self.parse_question(self.prompt)
    
    def prompt_func(self, identity) -> str:
        """
        Process the input_data and return the processed prompt.
        
        Args:
            question_ori: The question to be processed.
        
        Returns:
            str: The processed prompt.
        """
        # print("`identity` is ignored!!!!!")

        prompt = self.prompt + """\nThe output should be given in order from left to right, top to bottom, with each element separated by a space and different lines separated by a comma.
Ensure that your final answer is wrapped in double square brackets,like this: [[1 3 2,2 1 3,3 2 1]]. Making sure the size of your answer should be same as the size of the Calcudoko."""
        return prompt 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def generator(self, size:int =6, group_size_range:tuple =(1,4), seed:int = None):
        generator = CalcudokuGenerator(n=size, group_size_range=group_size_range, seed=seed)
        self.grid = generator.generate_puzzle()
        return self.grid

    def get_question(self):
        return f"""You are an intelligent assistant specializing in solving Calcudoko puzzles.

Calcudoko is a sudoku-like game played on an NxN grid. Fill each row and column with numbers from 1 to N, with no repeated number in any row or column. Each cage has a target number and an operator; the values in the cage must satisfy that operation.

The puzzle spec is:
{self.grid}

Provide the corresponding numbers for all positions in the Calcudoko."""


    @staticmethod
    def parse_question(question: str) -> dict:
        # 匹配谜题规格的数组部分
        match = re.search(r"\[(?:'[^']*'[,\s]*)*\]", question)
        if not match:
            return None
        array_str = match.group(0)
        try:
            puzzle_spec = ast.literal_eval(array_str)
        except:
            return None

        puzzle_rows = [row.split() for row in puzzle_spec]
        n = len(puzzle_rows)
        for row in puzzle_rows:
            if len(row) != n:
                return None

        groups: Dict[str, tuple] = {}
        puzzle_grid: List[List[str]] = []
        for row in puzzle_rows:
            grid_row = []
            for cell in row:
                group_char = cell[0]
                grid_row.append(group_char)
                # 提取运算符和目标值（如果有的话）
                op_match = re.fullmatch(r'^[A-Za-z]([+*/-])(\d+)$', cell)
                if op_match and group_char not in groups:
                    op = op_match.group(1)
                    target = int(op_match.group(2))
                    groups[group_char] = (op, target)
            puzzle_grid.append(grid_row)

        return {
            'groups': groups,
            'grid': puzzle_grid,
            'size': n
        }

    @staticmethod
    def check_solution(parsed_question: dict, parsed_response: dict) -> bool:
        n = parsed_question['size']
        grid = parsed_question['grid']
        groups = parsed_question['groups']
        solution = parsed_response

        # 检查行和列的有效性
        if len(solution) != n or any(len(row) != n for row in solution):
            return False
        for i in range(n):
            if sorted(solution[i]) != list(range(1, n+1)):
                return False
            col = [solution[j][i] for j in range(n)]
            if sorted(col) != list(range(1, n+1)):
                return False

        # 构建分组数字映射
        group_numbers = {}
        for i in range(n):
            for j in range(n):
                group = grid[i][j]
                num = solution[i][j]
                if group not in group_numbers:
                    group_numbers[group] = []
                group_numbers[group].append(num)

        # 验证每个分组
        for group, info in groups.items():
            nums = group_numbers.get(group, [])
            op, target = info

            if op == '+':
                if sum(nums) != target:
                    return False
            elif op == '*':
                product = 1
                for num in nums:
                    product *= num
                if product != target:
                    return False
            elif op == '-':
                total = sum(nums)
                if not any(2*x == total + target for x in nums):
                    return False
            elif op == '/':
                for x in nums:
                    product = 1
                    for num in nums:
                        if num != x:
                            product *= num
                    if product != 0 and x / product == target:
                        break
                else:
                    return False
            else:
                return False

        return True
