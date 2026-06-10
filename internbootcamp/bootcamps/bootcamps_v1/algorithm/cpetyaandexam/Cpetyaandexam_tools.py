import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cpetyaandexam.Cpetyaandexam_reward_calculator import CpetyaandexamRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CpetyaandexamVerificationTool(BaseTool):
    """Cpetyaandexam验证工具"""
    
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
            score = CpetyaandexamRewardCalculator.verify_score(
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
            logger.error(f"CpetyaandexamVerificationTool执行错误: {str(e)}")
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
    def solve_case(n, T, a, b, types, times):
        combined = sorted(zip(times, types), key=lambda x: (x[0], x[1]))
        sorted_times = [x[0] for x in combined]
        sorted_types = [x[1] for x in combined]

        # 计算前缀时间和剩余easy数量
        prefix = []
        total_time = 0
        for typ in sorted_types:
            total_time += a if typ == 0 else b
            prefix.append(total_time)

        max_points = 0

        # 情况1：解决所有问题
        if prefix[-1] <= T:
            return n

        # 情况2：在第一个问题强制前解决easy
        first_mandatory = sorted_times[0]
        if first_mandatory > 0:
            available = first_mandatory - 1
            max_easy = min(available // a, sum(1 for t in sorted_types if t == 0))
            max_points = max(max_points, max_easy)

        # 预处理剩余easy数量
        remaining_easy = [0] * (n + 1)
        count = 0
        for i in range(n-1, -1, -1):
            if sorted_types[i] == 0:
                count += 1
            remaining_easy[i] = count

        # 检查每个可能的分割点
        current_total_time = 0
        for i in range(n):
            current_total_time += a if sorted_types[i] == 0 else b
            if current_total_time > T:
                break

            # 计算后续可用时间
            next_mandatory = sorted_times[i+1] if i < n-1 else T + 1
            available_time = next_mandatory - current_total_time - 1
            if available_time < 0:
                continue

            # 计算可添加的easy数量
            possible = min(available_time // a, remaining_easy[i+1])
            max_points = max(max_points, i + 1 + possible)

        return max_points
