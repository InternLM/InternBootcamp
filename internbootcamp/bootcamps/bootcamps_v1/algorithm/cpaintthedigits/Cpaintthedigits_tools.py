import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpaintthedigits.Cpaintthedigits_reward_calculator import CpaintthedigitsRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CpaintthedigitsVerificationTool(BaseTool):
    """Cpaintthedigits验证工具"""
    
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
            score = CpaintthedigitsRewardCalculator.verify_score(
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
            logger.error(f"CpaintthedigitsVerificationTool执行错误: {str(e)}")
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
    def generate_non_decreasing(self, length):
        if length == 0:
            return []
        sequence = [random.randint(0, 9)]
        for _ in range(length-1):
            sequence.append(random.randint(sequence[-1], 9))
        return sequence

    @staticmethod
    def solve(N, A):
        B = ['1'] * N
        last_1 = -1
        transition_point = None
        last_2 = -1

        for i in range(N):
            current = A[i]

            if last_1 == -1:
                last_1 = current
                continue

            if current >= last_1:
                last_1 = current
                continue

            if transition_point is None:
                # Find transition point
                transition_point = i
                min_2_val = current
                for m in range(current + 1, 10):
                    for j in range(i):
                        if A[j] == m and B[j] == '1':
                            transition_point = j
                            min_2_val = m
                            break
                    else:
                        continue
                    break
                else:
                    return '-'

                # Update colors for transition segment
                for j in range(transition_point):
                    if A[j] >= min_2_val:
                        B[j] = '2'
                last_2 = max(A[transition_point:i], default=-1)
                last_1 = current
            else:
                if current < last_1 or (current > last_2 and last_2 != -1):
                    return '-'
                if current >= last_2:
                    B[i] = '2'
                    last_2 = current
                else:
                    last_1 = current
        return ''.join(B)
