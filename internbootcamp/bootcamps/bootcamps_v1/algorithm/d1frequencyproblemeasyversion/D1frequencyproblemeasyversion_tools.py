import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.d1frequencyproblemeasyversion.D1frequencyproblemeasyversion_reward_calculator import D1frequencyproblemeasyversionRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class D1frequencyproblemeasyversionVerificationTool(BaseTool):
    """D1frequencyproblemeasyversion验证工具"""
    
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
            score = D1frequencyproblemeasyversionRewardCalculator.verify_score(
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
            logger.error(f"D1frequencyproblemeasyversionVerificationTool执行错误: {str(e)}")
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
    def calculate_answer(a):
        """完全对齐参考代码的实现逻辑"""
        freq = defaultdict(int)
        for num in a:
            freq[num] += 1
        if not freq:
            return 0

        # 确定最大频率元素
        mx = max(freq.values())
        cnt = sum(1 for v in freq.values() if v == mx)
        ele = next(k for k, v in freq.items() if v == mx)

        # Case 1: 多个元素达到最大频率
        if cnt >= 2:
            return len(a)

        # Case 2: 单个最大频率元素时
        max_length = 0
        for candidate in range(1, 101):
            if candidate == ele:
                continue

            # 使用前缀和算法查找最长子数组
            prefix_sum = {0: -1}
            current_sum = 0
            for idx, num in enumerate(a):
                if num == ele:
                    current_sum += 1
                elif num == candidate:
                    current_sum -= 1

                if current_sum in prefix_sum:
                    max_length = max(max_length, idx - prefix_sum[current_sum])
                else:
                    prefix_sum[current_sum] = idx

        return max_length
