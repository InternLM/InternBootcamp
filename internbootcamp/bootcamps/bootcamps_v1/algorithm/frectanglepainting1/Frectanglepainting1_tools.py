import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.frectanglepainting1.Frectanglepainting1_reward_calculator import Frectanglepainting1RewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Frectanglepainting1VerificationTool(BaseTool):
    """Frectanglepainting1验证工具"""
    
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
            score = Frectanglepainting1RewardCalculator.verify_score(
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
            logger.error(f"Frectanglepainting1VerificationTool执行错误: {str(e)}")
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
    def calculate_min_cost(grid):
        n = len(grid)
        memo = {}

        def solve(r1, c1, r2, c2):
            if r1 > r2 or c1 > c2:
                return 0
            key = (r1, c1, r2, c2)
            if key in memo:
                return memo[key]

            # 优化全白判断
            has_black = False
            for i in range(r1, r2+1):
                if '#' in grid[i][c1:c2+1]:
                    has_black = True
                    break
            if not has_black:
                memo[key] = 0
                return 0

            min_cost = max(r2-r1+1, c2-c1+1)

            # 水平分割优化
            for i in range(r1, r2):
                cost = solve(r1, c1, i, c2) + solve(i+1, c1, r2, c2)
                if cost < min_cost:
                    min_cost = cost
                    if min_cost == 1:  # 提前终止
                        break

            # 垂直分割优化
            for j in range(c1, c2):
                cost = solve(r1, c1, r2, j) + solve(r1, j+1, r2, c2)
                if cost < min_cost:
                    min_cost = cost
                    if min_cost == 1:
                        break

            memo[key] = min_cost
            return min_cost

        return solve(0, 0, n-1, n-1)
