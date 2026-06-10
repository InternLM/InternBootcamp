import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dweirdchess.Dweirdchess_reward_calculator import DweirdchessRewardCalculator

# 导入依赖库
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DweirdchessVerificationTool(BaseTool):
    """Dweirdchess验证工具"""
    
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
            score = DweirdchessRewardCalculator.verify_score(
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
            logger.error(f"DweirdchessVerificationTool执行错误: {str(e)}")
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
    def _generate_move_vectors(self, n):
        if self.current_move_type == 'rook':
            vectors = []
            for dx in range(-n+1, n):
                if dx != 0:
                    vectors.append((dx, 0))
            for dy in range(-n+1, n):
                if dy != 0:
                    vectors.append((0, dy))
            return list(set(vectors))
        elif self.current_move_type == 'knight':
            return [ (dx, dy) for dx in (-2, -1, 1, 2) for dy in (-2, -1, 1, 2) if abs(dx) + abs(dy) == 3 ]
        else:
            vectors = []
            for _ in range(random.randint(3, 6)):
                dx = random.randint(-n+1, n-1)
                dy = random.randint(-n+1, n-1)
                if dx == 0 and dy == 0:
                    continue
                vectors.append((dx, dy))
            return list(set(vectors))

    def _generate_o_positions(self, n):
        count = random.randint(self.min_o, self.max_o)
        positions = set()
        while len(positions) < count:
            x = random.randint(0, n-1)
            y = random.randint(0, n-1)
            positions.add((x, y))
        return list(positions)

    def _generate_grid(self, n, o_positions, move_vectors):
        grid = [['.' for _ in range(n)] for _ in range(n)]
        o_coords = set((x, y) for x, y in o_positions)

        for x, y in o_coords:
            grid[y][x] = 'o'

        for x, y in o_coords:
            for dx, dy in move_vectors:
                tx = x + dx
                ty = y + dy
                if 0 <= tx < n and 0 <= ty < n:
                    if (tx, ty) not in o_coords:
                        grid[ty][tx] = 'x'

        return grid
