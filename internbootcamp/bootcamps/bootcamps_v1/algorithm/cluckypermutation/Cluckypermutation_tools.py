import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cluckypermutation.Cluckypermutation_reward_calculator import CluckypermutationRewardCalculator

# 导入依赖库
from math import factorial
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CluckypermutationVerificationTool(BaseTool):
    """Cluckypermutation验证工具"""
    
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
            score = CluckypermutationRewardCalculator.verify_score(
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
            logger.error(f"CluckypermutationVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def calculate_answer(cls, n, k):
        # 验证排列是否存在
        m = 1
        while True:
            try:
                if factorial(m) >= k:
                    break
                m += 1
                if m > min(20, n+1):  # 防止无限循环
                    break
            except OverflowError:
                break
        if m > n:
            return -1

        # 生成排列后缀部分
        suffix = list(range(n-m+1, n+1))
        remaining_k = k
        for i in range(m):
            available = sorted(suffix[i:])
            slot_size = factorial(m - i - 1)

            # 计算当前块的位置
            pos = 0
            while remaining_k > slot_size:
                remaining_k -= slot_size
                pos += 1
                if pos >= len(available):
                    return -1  # 防止越界

            # 交换元素位置
            available[0], available[pos] = available[pos], available[0]
            # 保持后续元素有序
            suffix = suffix[:i] + available

        # 计算幸运数数量
        count = cls.count_lucky_numbers(n - m)

        # 检查后缀部分
        for idx, num in enumerate(suffix, start=n-m+1):
            if cls.is_lucky(idx) and cls.is_lucky(num):
                count += 1

        return count

    @staticmethod
    def is_lucky(x):
        return x > 0 and all(c in {'4', '7'} for c in str(x))

    @classmethod
    def count_lucky_numbers(cls, max_num):
        """使用BFS生成所有幸运数"""
        count = 0
        queue = ['4', '7']
        while queue:
            num = queue.pop(0)
            value = int(num)
            if value > max_num:
                continue
            count += 1
            queue.append(num + '4')
            queue.append(num + '7')
        return count
