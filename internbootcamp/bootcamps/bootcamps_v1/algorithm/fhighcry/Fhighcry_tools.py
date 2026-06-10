import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fhighcry.Fhighcry_reward_calculator import FhighcryRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class FhighcryVerificationTool(BaseTool):
    """Fhighcry验证工具"""
    
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
            score = FhighcryRewardCalculator.verify_score(
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
            logger.error(f"FhighcryVerificationTool执行错误: {str(e)}")
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
    def _compute_answer(n, A):
        if n < 2: return 0

        # 原参考代码的实现保持不变
        L = [-1]*n
        stack = []
        for i in range(n):
            while stack and A[stack[-1]] < A[i]:
                stack.pop()
            L[i] = stack[-1] if stack else -1
            stack.append(i)

        R = [n]*n
        stack = []
        for i in reversed(range(n)):
            while stack and A[stack[-1]] <= A[i]:
                stack.pop()
            R[i] = stack[-1] if stack else n
            stack.append(i)

        L2 = [-1]*n
        last = [-1]*60
        for i in range(n):
            x = -1
            a = A[i]
            for j in range(60):
                if a & (1 << j):
                    last[j] = i
                else:
                    if last[j] > x:
                        x = last[j]
            L2[i] = max(L[i], x)

        R2 = [n]*n
        last = [n]*60
        for i in reversed(range(n)):
            x = n
            a = A[i]
            for j in range(60):
                if a & (1 << j):
                    last[j] = i
                else:
                    if last[j] < x:
                        x = last[j]
            R2[i] = min(R[i], x)

        ans = 0
        for i in range(n):
            ans += (L2[i]-L[i])*(R[i]-i) + (i-L[i])*(R[i]-R2[i]) - (L2[i]-L[i])*(R[i]-R2[i])
        return ans
