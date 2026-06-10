import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dnashmatrix.Dnashmatrix_reward_calculator import DnashmatrixRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DnashmatrixVerificationTool(BaseTool):
    """Dnashmatrix验证工具"""
    
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
            score = DnashmatrixRewardCalculator.verify_score(
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
            logger.error(f"DnashmatrixVerificationTool执行错误: {str(e)}")
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
    def generate_valid_case(self):
        """生成有效案例并标记is_valid=True"""
        grid = self.generate_valid_grid()
        valid_cells = self.simulate_grid(grid)
        return {
            "n": self.n,
            "cells": valid_cells,
            "is_valid": True
        }

    def generate_invalid_case(self):
        """生成无效案例并标记is_valid=False"""
        n = self.n
        # 创建一个必定矛盾的案例：所有单元格要求最终到达同一个X但路径冲突
        valid_grid = self.generate_valid_grid()
        cells = self.simulate_grid(valid_grid)
        # 随机选择一个单元格，强制其终止点为另一个单元格，但该单元格并非X且路径无法到达
        i, j = random.randint(0, n-1), random.randint(0, n-1)
        target = (random.randint(1, n), random.randint(1, n))
        while target == (i+1, j+1) or valid_grid[i][j] == 'X':
            i, j = random.randint(0, n-1), random.randint(0, n-1)
            target = (random.randint(1, n), random.randint(1, n))
        cells[i][j] = target
        return {
            "n": n,
            "cells": cells,
            "is_valid": False  # 强制标记为无效
        }

    def generate_valid_grid(self):
        """生成合法网格，确保指令不会导致越界"""
        grid = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                possible = []
                if i > 0:
                    possible.append('U')
                if i < self.n - 1:
                    possible.append('D')
                if j > 0:
                    possible.append('L')
                if j < self.n - 1:
                    possible.append('R')
                possible.append('X')
                # 优先设置X的概率
                if random.random() < self.x_prob:
                    char = 'X'
                else:
                    char = random.choice(possible)
                row.append(char)
            grid.append(row)
        return grid

    def simulate_grid(self, grid):
        """计算每个单元格的终止点"""
        cells = []
        for i in range(self.n):
            row = []
            for j in range(self.n):
                termination = self.simulate_cell(i, j, grid)
                row.append(termination)
            cells.append(row)
        return cells

    def simulate_cell(self, r, c, grid):
        """模拟玩家移动，返回终止点或(-1,-1)"""
        visited = set()
        current_r, current_c = r, c
        while True:
            if (current_r, current_c) in visited:
                return (-1, -1)
            visited.add((current_r, current_c))
            char = grid[current_r][current_c]
            if char == 'X':
                return (current_r + 1, current_c + 1)
            elif char == 'U':
                current_r -= 1
            elif char == 'D':
                current_r += 1
            elif char == 'L':
                current_c -= 1
            elif char == 'R':
                current_c += 1

    @classmethod
    def check_valid_solution(cls, solution_lines, identity):
        """验证有效案例的网格正确性"""
        n = identity["n"]
        if len(solution_lines) != n + 1:
            return False
        grid = solution_lines[1:]
        # 格式检查
        for row in grid:
            if len(row) != n or any(c not in "UDLRX" for c in row):
                return False
        # 指令合法性检查
        for i in range(n):
            for j in range(n):
                c = grid[i][j]
                if (c == 'U' and i == 0) or (c == 'D' and i == n-1) or \
                   (c == 'L' and j == 0) or (c == 'R' and j == n-1):
                    return False
        # 终止点一致性检查
        for i in range(n):
            for j in range(n):
                simulated = cls.static_simulate_cell(i, j, grid)
                expected = identity["cells"][i][j]
                if simulated != expected:
                    return False
        return True

    @staticmethod
    def static_simulate_cell(r, c, grid):
        """静态方法：模拟单元格移动"""
        n = len(grid)
        visited = set()
        current_r, current_c = r, c
        while True:
            if (current_r, current_c) in visited:
                return (-1, -1)
            visited.add((current_r, current_c))
            char = grid[current_r][current_c]
            if char == 'X':
                return (current_r + 1, current_c + 1)
            elif char == 'U':
                current_r -= 1
            elif char == 'D':
                current_r += 1
            elif char == 'L':
                current_c -= 1
            elif char == 'R':
                current_c += 1
