import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccompartments.Ccompartments_reward_calculator import CcompartmentsRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcompartmentsVerificationTool(BaseTool):
    """Ccompartments验证工具"""
    
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
            score = CcompartmentsRewardCalculator.verify_score(
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
            logger.error(f"CcompartmentsVerificationTool执行错误: {str(e)}")
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
    def compute_min_persuasion(a):
        counts = [0] * 5
        for num in a:
            counts[num] += 1
        res = 0

        # Pair 1s and 2s optimally
        t = min(counts[1], counts[2])
        res += t
        counts[1] -= t
        counts[2] -= t
        counts[3] += t

        # Process remaining 1s or 2s
        if counts[1] > 0:
            # Handle groups of 3 remaining 1s
            t = counts[1] // 3
            res += t * 2
            counts[3] += t
            counts[1] %= 3
        elif counts[2] > 0:
            # Handle groups of 3 remaining 2s
            t = counts[2] // 3
            res += t * 2
            counts[3] += t * 2
            counts[2] %= 3

        remaining_1 = counts[1]
        remaining_2 = counts[2]

        # Handle remaining cases
        if remaining_1 == 0:
            if remaining_2 == 1:
                if counts[4] >= 1:
                    res += 1
                elif counts[3] >= 2:
                    res += 2
                else:
                    return -1
            elif remaining_2 == 2:
                res += 2
            elif remaining_2 > 0:
                return -1
        elif remaining_1 == 1:
            if remaining_2 == 1:
                res += 1
            elif remaining_2 == 2:
                if counts[4] >= 1:
                    res += 2
                elif counts[3] >= 1:
                    res += 3
                else:
                    return -1
            elif remaining_2 == 0:
                if counts[3] >= 1:
                    res += 1
                elif counts[4] >= 2:
                    res += 2
                else:
                    return -1
            else:
                return -1
        elif remaining_1 == 2:
            if remaining_2 == 0:
                if counts[4] >= 1:
                    res += 2
                elif counts[3] >= 2:
                    res += 2
                else:
                    return -1
            elif remaining_2 in (1, 2):
                res += 2
            else:
                return -1
        else:
            return -1

        # Check if any remaining students after processing
        if counts[1] > 0 or counts[2] > 0:
            return -1
        return res
