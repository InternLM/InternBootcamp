import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.tents.tents_reward_calculator import TentsRewardCalculator

# 导入依赖库
import random
import re
import ast
from typing import List
from typing import Tuple



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class TentsVerificationTool(BaseTool):
    """Tents验证工具"""
    
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
            score = TentsRewardCalculator.verify_score(
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
            logger.error(f"TentsVerificationTool执行错误: {str(e)}")
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
    def _generate_tent_positions(self) -> List[Tuple[int, int]]:
        available = [[True for _ in range(self.cols)] for _ in range(self.rows)]
        tents = []
        positions = [(i, j) for i in range(self.rows) for j in range(self.cols)]
        random.shuffle(positions)

        for x, y in positions:
            if available[x][y]:
                tents.append((x, y))
                # Mark surrounding cells as unavailable
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = x+dx, y+dy
                        if 0 <= nx < self.rows and 0 <= ny < self.cols:
                            available[nx][ny] = False
        return tents

    def _place_trees(self, tent_positions) -> Tuple[List[List[int]], List[Tuple[int, int]]]:
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        tree_positions = []

        for x, y in tent_positions:
            directions = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
            random.shuffle(directions)
            placed = False
            for dx, dy in directions:
                if 0 <= dx < self.rows and 0 <= dy < self.cols:
                    if grid[dx][dy] == 0 and (dx, dy) not in tent_positions:
                        grid[dx][dy] = 1
                        tree_positions.append((dx, dy))
                        placed = True
                        break
            if not placed:
                return None, None
        return grid, tree_positions

    def _validate_tree_tents(self, grid, tents, trees) -> bool:
        # Check tent adjacency
        for i in range(len(tents)):
            for j in range(i+1, len(tents)):
                x1, y1 = tents[i]
                x2, y2 = tents[j]
                if abs(x1 - x2) <= 1 and abs(y1 - y2) <= 1:
                    return False

        # Check tree-tent mapping
        tree_counts = {(i,j):0 for i in range(self.rows) for j in range(self.cols) if grid[i][j]}
        for x, y in tents:
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < self.rows and 0 <= ny < self.cols:
                    if grid[nx][ny]:
                        tree_counts[(nx, ny)] += 1
        return all(c == 1 for c in tree_counts.values())
