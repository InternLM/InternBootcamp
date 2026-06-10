import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ejeffandbrackets.Ejeffandbrackets_reward_calculator import EjeffandbracketsRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EjeffandbracketsVerificationTool(BaseTool):
    """Ejeffandbrackets验证工具"""
    
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
            score = EjeffandbracketsRewardCalculator.verify_score(
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
            logger.error(f"EjeffandbracketsVerificationTool执行错误: {str(e)}")
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
    def compute_min_ink(n, m, a, b):
        class Uzi:
            def __init__(self):
                self.A = [[float('inf')] * 41 for _ in range(41)]

        def multiply(a_mat, b_mat):
            res = Uzi()
            for i in range(41):
                for j in range(41):
                    min_val = float('inf')
                    for k in range(41):
                        if a_mat.A[i][k] + b_mat.A[k][j] < min_val:
                            min_val = a_mat.A[i][k] + b_mat.A[k][j]
                    res.A[i][j] = min_val
            return res

        G = Uzi()
        for i in range(41):
            dp = [[float('inf')] * 41 for _ in range(n+1)]
            dp[0][i] = 0
            for j in range(1, n+1):
                for k in range(41):
                    if dp[j-1][k] == float('inf'):
                        continue
                    # Open bracket
                    if k < 40:
                        new_k = k + 1
                        cost = a[(j-1) % n]  # Fixed modulo position
                        if dp[j][new_k] > dp[j-1][k] + cost:
                            dp[j][new_k] = dp[j-1][k] + cost
                    # Close bracket
                    if k > 0:
                        new_k = k - 1
                        cost = b[(j-1) % n]  # Fixed modulo position
                        if dp[j][new_k] > dp[j-1][k] + cost:
                            dp[j][new_k] = dp[j-1][k] + cost
            for k in range(41):
                G.A[i][k] = dp[n][k]

        # Matrix exponentiation
        result = Uzi()
        for i in range(41):
            result.A[i][i] = 0
        exponent = m
        current = G
        while exponent > 0:
            if exponent % 2 == 1:
                result = multiply(result, current)
            current = multiply(current, current)
            exponent = exponent // 2
        return result.A[0][0]
