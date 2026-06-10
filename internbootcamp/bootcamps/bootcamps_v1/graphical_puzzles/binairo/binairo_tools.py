import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.binairo.binairo_reward_calculator import BinairoRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BinairoVerificationTool(BaseTool):
    """Binairo验证工具"""
    
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
            score = BinairoRewardCalculator.verify_score(
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
            logger.error(f"BinairoVerificationTool执行错误: {str(e)}")
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
    def generate_solution(self):
        n = self.size
        possible_rows = self.generate_all_possible_rows(n)
        random.shuffle(possible_rows)

        for _ in range(1000):
            try:
                selected = random.sample(possible_rows, n)
            except ValueError:
                continue

            if len({tuple(r) for r in selected}) != n:
                continue

            if self.check_columns(selected, n):
                return selected

        # Fallback example for 4x4
        return [
            [0, 1, 0, 1],
            [1, 0, 1, 0],
            [0, 1, 1, 0],
            [1, 0, 0, 1]
        ]

    def generate_all_possible_rows(self, n):
        return self.backtrack_row([], n, n//2, n//2)

    def backtrack_row(self, current, n, zeros, ones):
        if len(current) == n:
            return [current.copy()] if zeros == 0 and ones == 0 else []

        solutions = []
        for bit in [0, 1]:
            if (bit == 0 and zeros == 0) or (bit == 1 and ones == 0):
                continue

            if len(current) >= 2 and current[-1] == bit and current[-2] == bit:
                continue

            new_current = current.copy()
            new_current.append(bit)
            new_zeros = zeros - 1 if bit == 0 else zeros
            new_ones = ones - 1 if bit == 1 else ones
            solutions += self.backtrack_row(new_current, n, new_zeros, new_ones)

        return solutions

    def check_columns(self, grid, n):
        columns = list(zip(*grid))
        for col in columns:
            if col.count(0) != n//2 or col.count(1) != n//2:
                return False
            for i in range(len(col)-2):
                if col[i] == col[i+1] == col[i+2]:
                    return False
        return len(set(columns)) == len(columns)
