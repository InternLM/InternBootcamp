import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.drectanglepainting1.Drectanglepainting1_reward_calculator import Drectanglepainting1RewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class Drectanglepainting1VerificationTool(BaseTool):
    """Drectanglepainting1验证工具"""
    
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
            score = Drectanglepainting1RewardCalculator.verify_score(
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
            logger.error(f"Drectanglepainting1VerificationTool执行错误: {str(e)}")
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
    def compute_min_cost(n, grid):
        # 初始化前缀和数组（从1开始索引）
        f = [[0]*(n+2) for _ in range(n+2)]
        for i in range(1, n+1):
            for j in range(1, n+1):
                cell_value = 1 if grid[i-1][j-1] == '#' else 0
                f[i][j] = f[i-1][j] + f[i][j-1] - f[i-1][j-1] + cell_value

        # 初始化四维DP数组
        d = [[[[0]*(n+2) for _ in range(n+2)] 
             for __ in range(n+2)] 
             for ___ in range(n+2)]

        # 动态规划计算
        for i in range(n, 0, -1):
            for j in range(n, 0, -1):
                for ii in range(i, n+1):
                    for jj in range(j, n+1):
                        # 计算当前区域的黑块总数
                        total = f[ii][jj] - f[i-1][jj] - f[ii][j-1] + f[i-1][j-1]

                        if total == 0:
                            d[i][j][ii][jj] = 0
                            continue

                        # 初始值为区域的最大边长
                        h = ii - i + 1
                        w = jj - j + 1
                        val = max(h, w)

                        # 垂直切分尝试
                        for k in range(j, jj):
                            val = min(val, d[i][j][ii][k] + d[i][k+1][ii][jj])

                        # 水平切分尝试
                        for k in range(i, ii):
                            val = min(val, d[i][j][k][jj] + d[k+1][j][ii][jj])

                        d[i][j][ii][jj] = val

        return d[1][1][n][n]
