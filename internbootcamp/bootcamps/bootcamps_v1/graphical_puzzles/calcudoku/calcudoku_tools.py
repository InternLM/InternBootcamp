import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.calcudoku.calcudoku_reward_calculator import CalcudokuRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.calcudoku.lib.calcudoku_generator import CalcudokuGenerator
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CalcudokuVerificationTool(BaseTool):
    """Calcudoku验证工具"""
    
    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        
    async def create(self, instance_id: Optional[str] = None, identity: dict = None, **kwargs) -> str:
        """创建工具实例"""
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "identity": identity,
            "verification_history": [],
            "verification_count": 0
        }
        return instance_id

    @rollout_trace_op
    async def execute(self, instance_id: str, parameters: dict[str, Any], **kwargs) -> Tuple[str, float, dict]:
        """执行验证"""
        try:
            solution = parameters.get("solution", {})
            
            if not solution:
                return "错误: 缺少解决方案", -0.1, {}
            
            # 获取任务身份信息
            identity = self._instance_dict[instance_id]["identity"]
            
            # 使用奖励计算器验证解决方案
            score = CalcudokuRewardCalculator.verify_score(
                model_output=json.dumps(solution), 
                identity=identity
            )
            
            # 更新实例状态
            self._instance_dict[instance_id]["verification_count"] += 1
            verification_result = {
                "solution": solution,
                "score": score,
                "timestamp": self._instance_dict[instance_id]["verification_count"]
            }
            self._instance_dict[instance_id]["verification_history"].append(verification_result)
            
            # 构建响应
            if score == 1.0:
                response = "✓ 解决方案验证成功！所有约束条件均满足。"
                reward = 1.0
            elif score > 0.0:
                response = f"⚠ 解决方案部分正确，得分: {score:.2f}/1.0"
                reward = score * 0.5
            else:
                response = f"✗ 解决方案验证失败，得分: {score:.2f}/1.0"
                reward = -0.1
            
            metrics = {
                "solution": solution,
                "verification_score": score,
                "verification_count": self._instance_dict[instance_id]["verification_count"],
                "is_correct": score == 1.0
            }
            
            return response, reward, metrics
            
        except Exception as e:
            logger.error(f"CalcudokuVerificationTool执行错误: {str(e)}")
            return f"验证执行错误: {str(e)}", -0.1, {"error": str(e)}

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        """计算累计工具奖励"""
        if instance_id not in self._instance_dict:
            return 0.0
        
        history = self._instance_dict[instance_id]["verification_history"]
        if not history:
            return 0.0
        
        # 返回最高验证分数
        max_score = max(item["score"] for item in history)
        return min(max_score, 1.0)
    
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
