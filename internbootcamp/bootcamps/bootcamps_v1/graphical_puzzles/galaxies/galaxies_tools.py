import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.galaxies.galaxies_reward_calculator import GalaxiesRewardCalculator

# 导入依赖库
import re
from ast import literal_eval
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class GalaxiesVerificationTool(BaseTool):
    """Galaxies验证工具"""
    
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
            score = GalaxiesRewardCalculator.verify_score(
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
            logger.error(f"GalaxiesVerificationTool执行错误: {str(e)}")
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
    @staticmethod
    def _validate_structure(solution):
        """Validate basic solution structure"""
        if not isinstance(solution, list):
            return False
        for g in solution:
            if not isinstance(g, dict) or 'center' not in g or 'cells' not in g:
                return False
            if not isinstance(g['cells'], list) or len(g['cells']) == 0:
                return False
        return True

    @staticmethod
    def _check_centers(solution, expected_centers):
        """Verify all expected centers are present"""
        solution_centers = {tuple(g['center']) for g in solution}
        expected_set = {tuple(c) for c in expected_centers}
        return solution_centers == expected_set

    @staticmethod
    def _check_coverage(solution, rows, cols):
        """Verify complete grid coverage without overlaps"""
        all_cells = []
        for g in solution:
            all_cells.extend(map(tuple, g['cells']))
        expected = {(r, c) for r in range(rows) for c in range(cols)}
        return len(all_cells) == len(expected) and set(all_cells) == expected

    @classmethod
    def _validate_galaxy(cls, galaxy):
        """Validate individual galaxy constraints"""
        cells = [tuple(c) for c in galaxy['cells']]
        center = tuple(galaxy['center'])

        # Check center presence
        if center not in cells:
            return False

        # Check symmetry
        cx, cy = center
        for (x, y) in cells:
            sym = (2*cx - x, 2*cy - y)
            if sym not in cells:
                return False

        # Check connectivity
        return cls._is_connected(cells)

    @staticmethod
    def _is_connected(cells):
        """BFS check for region connectivity"""
        if not cells:
            return False

        visited = set()
        q = deque([cells[0]])
        visited.add(cells[0])

        while q:
            x, y = q.popleft()
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                neighbor = (x+dx, y+dy)
                if neighbor in cells and neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)

        return len(visited) == len(cells)
