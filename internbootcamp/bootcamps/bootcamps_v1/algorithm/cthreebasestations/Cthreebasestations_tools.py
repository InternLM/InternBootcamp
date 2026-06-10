import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cthreebasestations.Cthreebasestations_reward_calculator import CthreebasestationsRewardCalculator

# 导入依赖库
from bisect import bisect_left
from bisect import bisect_right
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CthreebasestationsVerificationTool(BaseTool):
    """Cthreebasestations验证工具"""
    
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
            score = CthreebasestationsRewardCalculator.verify_score(
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
            logger.error(f"CthreebasestationsVerificationTool执行错误: {str(e)}")
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
    def _compute_solution(n, houses):
        a = sorted([x * 2 for x in houses])
        if not a:
            return 0.0, [0.0, 0.0, 0.0]

        left, right = 0, 1 << 31

        # 二分查找最小d
        while left < right:
            mid = (left + right) // 2
            s = mid * 2
            x = bisect_right(a, a[0] + s)
            y = bisect_left(a, a[-1] - s)

            if x < y and (a[y-1] - a[x] > s):
                left = mid + 1
            else:
                right = mid

        d = left
        correct_d = d / 2.0

        # 计算基站坐标
        x_val = bisect_right(a, a[0] + d * 2)
        y_val = bisect_left(a, a[-1] - d * 2)

        # 处理全范围覆盖的情况
        if x_val >= len(a):
            return correct_d, [a[0]/2.0, a[0]/2.0, a[0]/2.0]

        # 计算三段分割点
        s1 = (a[0] + a[x_val-1])/4.0 if x_val > 0 else a[0]/2.0
        s2 = (a[x_val] + a[y_val-1])/4.0 if x_val < y_val else s1
        s3 = (a[y_val] + a[-1])/4.0 if y_val < len(a) else a[-1]/2.0

        return correct_d, [s1, s2, s3]
