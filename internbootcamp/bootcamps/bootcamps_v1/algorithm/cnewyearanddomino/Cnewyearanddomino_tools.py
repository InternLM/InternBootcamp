import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cnewyearanddomino.Cnewyearanddomino_reward_calculator import CnewyearanddominoRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CnewyearanddominoVerificationTool(BaseTool):
    """Cnewyearanddomino验证工具"""
    
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
            score = CnewyearanddominoRewardCalculator.verify_score(
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
            logger.error(f"CnewyearanddominoVerificationTool执行错误: {str(e)}")
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
    def compute_answer(self, grid, query):
        h, w = len(grid), len(grid[0])
        r1, c1, r2, c2 = query

        # Build prefix sums for vertical dominoes
        d1 = defaultdict(int)
        for i in range(h+1):
            for j in range(w+1):
                if i <= 1 or j == 0:
                    d1[(i, j)] = 0
                else:
                    term = 1 if (i >= 2 and 
                                grid[i-1][j-1] == '.' and 
                                grid[i-2][j-1] == '.') else 0
                    d1[(i, j)] = d1[(i-1, j)] + d1[(i, j-1)] - d1[(i-1, j-1)] + term

        # Build prefix sums for horizontal dominoes
        d2 = defaultdict(int)
        for i in range(h+1):
            for j in range(w+1):
                if j <= 1 or i == 0:
                    d2[(i, j)] = 0
                else:
                    term = 1 if (j >= 2 and 
                                grid[i-1][j-1] == '.' and 
                                grid[i-1][j-2] == '.') else 0
                    d2[(i, j)] = d2[(i-1, j)] + d2[(i, j-1)] - d2[(i-1, j-1)] + term

        # Calculate sum for vertical dominoes
        def sum_vertical(r1, c1, r2, c2):
            a = d1.get((r1-1, c1-1), 0)
            b = d1.get((r1-1, c2), 0)
            c_val = d1.get((r2, c1-1), 0)
            d_val = d1.get((r2, c2), 0)
            return d_val - b - c_val + a

        # Calculate sum for horizontal dominoes
        def sum_horizontal(r1, c1, r2, c2):
            a = d2.get((r1-1, c1-1), 0)
            b = d2.get((r1-1, c2), 0)
            c_val = d2.get((r2, c1-1), 0)
            d_val = d2.get((r2, c2), 0)
            return d_val - b - c_val + a

        total = 0
        # Vertical dominoes (need at least 2 rows)
        if r2 >= r1 + 1:
            total += sum_vertical(r1+1, c1, r2, c2)
        # Horizontal dominoes (need at least 2 columns)
        if c2 >= c1 + 1:
            total += sum_horizontal(r1, c1+1, r2, c2)

        return total
