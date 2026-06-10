import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.campsite_reward_calculator import CampsiteRewardCalculator

# 导入依赖库
import re
import ast
import json
import sys
import random
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.lib.campsite_generator import generate_campsite
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.campsite.lib.campsite_validor import validate_campsite_solution



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CampsiteVerificationTool(BaseTool):
    """Campsite验证工具"""
    
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
            score = CampsiteRewardCalculator.verify_score(
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
            logger.error(f"CampsiteVerificationTool执行错误: {str(e)}")
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
    def generator(self, size:tuple = (8,8), expect_camp_number:int = 8, random_rate:float = 0.1 , seed:int = None):
        if size[0] < 2 and size[1] < 2:
            raise ValueError
        self.grid, self.row_constraints, self.col_constraints, self.refer_ans = generate_campsite(size[0], size[1], expect_camp_number, seed=seed, random_rate=random_rate)
        return self.grid, self.row_constraints, self.col_constraints    

    @staticmethod
    def check_solution(parsed_question: dict, parsed_response: dict) -> bool:
        original_grid = parsed_question['input_grid']
        expected_rows = parsed_question['row_constraints']
        expected_cols = parsed_question['col_constraints']
        solution = parsed_response

        n, m = len(original_grid), len(original_grid[0]) if original_grid else 0

        # Check dimensions
        if len(solution) != n or any(len(row) != m for row in solution):
            return False

        tents = []
        # Check T positions and collect tents
        for i in range(n):
            for j in range(m):
                orig = original_grid[i][j]
                sol = solution[i][j]
                if orig == 'T':
                    if sol != 'T':
                        return False
                else:
                    if sol not in ('X', 'C'):
                        return False
                    if sol == 'C':
                        tents.append((i, j))

        # Check tents adjacency to trees and other tents
        directions_ortho = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for i, j in tents:
            has_tree = False
            for dx, dy in directions_ortho:
                x, y = i + dx, j + dy
                if 0 <= x < n and 0 <= y < m and solution[x][y] == 'T':
                    has_tree = True
                    break
            if not has_tree:
                return False

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    x, y = i + dx, j + dy
                    if 0 <= x < n and 0 <= y < m and (x, y) in tents:
                        return False

        # Check row constraints
        for i in range(n):
            if sum(1 for cell in solution[i] if cell == 'C') != expected_rows[i]:
                return False

        # Check column constraints
        for j in range(m):
            if sum(1 for i in range(n) if solution[i][j] == 'C') != expected_cols[j]:
                return False

        return True
