import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccaptainmarmot.Ccaptainmarmot_reward_calculator import CcaptainmarmotRewardCalculator

# 导入依赖库
import math
import re
import random
from itertools import combinations



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcaptainmarmotVerificationTool(BaseTool):
    """Ccaptainmarmot验证工具"""
    
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
            score = CcaptainmarmotRewardCalculator.verify_score(
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
            logger.error(f"CcaptainmarmotVerificationTool执行错误: {str(e)}")
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
    def _generate_regiment(self, solvable=True):
        """Generate a regiment that can be solvable or unsolvable"""
        regiment = []
        origin_map = []

        # 1. Generate base points configuration
        if solvable:
            # Generate valid square points
            d = random.randint(1, 5)
            square_points = [
                (d, 0), (0, d), (-d, 0), (0, -d)
            ]
            random.shuffle(square_points)
        else:
            # Generate invalid points (non-square)
            square_points = [
                (random.randint(-5, 5), random.randint(-5, 5))
                for _ in range(4)
            ]
            # Ensure at least 3 points are collinear
            square_points[-1] = self._create_collinear_point(square_points[:3])

        # 2. Generate origins for each mole
        if self.same_origin:
            common_origin = (random.randint(-10, 10), random.randint(-10, 10))
            origin_map = [common_origin]*4
        else:
            origin_map = [(random.randint(-10, 10), random.randint(-10, 10)) 
                         for _ in range(4)]

        # 3. Apply rotations and build moles
        for idx in range(4):
            x_base, y_base = square_points[idx]
            a, b = origin_map[idx]

            # Apply random rotations
            rotations = random.randint(0, self.max_rotation)
            cx, cy = x_base, y_base
            for _ in range(rotations):
                nx = a - (cy - b)
                ny = b + (cx - a)
                cx, cy = nx, ny

            regiment.append((cx, cy, a, b))

        return regiment

    def _create_collinear_point(self, points):
        """Create a collinear point to make square impossible"""
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]

        # Find vector for points 0->1 and 0->2
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x3 - x1
        dy2 = y3 - y1

        # Ensure collinearity
        if dx1 * dy2 == dx2 * dy1:
            # Points are collinear, create another collinear point
            t = random.uniform(1.5, 3)
            return (x1 + t*dx1, y1 + t*dy1)
        else:
            # Force fourth point to be collinear
            t = random.uniform(0.5, 2)
            return (x2 + t*(x3 - x2), y2 + t*(y3 - y2))

    @staticmethod
    def _is_valid_square(points):
        # Calculate all pairwise squared distances
        dists = []
        for (x1, y1), (x2, y2) in combinations(points, 2):
            dist_sq = (x2-x1)**2 + (y2-y1)**2
            dists.append(dist_sq)

        # Verify square properties: 2 distinct distances (sides and diagonals)
        dists.sort()
        return (
            len(dists) == 6 and
            dists[0] == dists[1] == dists[2] == dists[3] and  # 4 equal sides
            dists[4] == dists[5] and                          # 2 equal diagonals
            dists[4] == 2 * dists[0] and                      # Diagonal = side*sqrt(2)
            dists[0] > 0                                      # Non-degenerate
        )

    @classmethod
    def _verify_single_regiment(cls, answer, regiment):
        """Verify single regiment answer"""
        rotation_states = []
        for mole in regiment:
            x, y, a, b = mole
            states = []
            current_x, current_y = x, y
            states.append((current_x, current_y))
            for _ in range(3):
                current_x, current_y = a - (current_y - b), b + (current_x - a)
                states.append((current_x, current_y))
            rotation_states.append(states)

        min_rotations = None
        for r0 in range(4):
            for r1 in range(4):
                for r2 in range(4):
                    for r3 in range(4):
                        points = [
                            rotation_states[0][r0],
                            rotation_states[1][r1],
                            rotation_states[2][r2],
                            rotation_states[3][r3]
                        ]
                        if cls._is_valid_square(points):
                            total = r0 + r1 + r2 + r3
                            if min_rotations is None or total < min_rotations:
                                min_rotations = total

        correct = min_rotations if min_rotations is not None else -1
        return answer == correct
