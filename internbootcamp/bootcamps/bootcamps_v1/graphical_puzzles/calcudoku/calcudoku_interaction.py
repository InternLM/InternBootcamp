from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.calcudoku.calcudoku_reward_calculator import CalcudokuRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.calcudoku.lib.calcudoku_generator import CalcudokuGenerator
import random




class CalcudokuInteraction(BaseInteraction):
    """Calcudoku交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = CalcudokuRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个calcudoku问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
    # 其他额外方法
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
