import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clittleelephantandshifts.Clittleelephantandshifts_reward_calculator import ClittleelephantandshiftsRewardCalculator

# 导入依赖库
import random
from heapq import heappop
from heapq import heappush



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ClittleelephantandshiftsVerificationTool(BaseTool):
    """Clittleelephantandshifts验证工具"""
    
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
            score = ClittleelephantandshiftsRewardCalculator.verify_score(
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
            logger.error(f"ClittleelephantandshiftsVerificationTool执行错误: {str(e)}")
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
    def compute_expected(n, a, b):
        # Convert to 0-based and precompute positions in a
        a_pos = {num: idx for idx, num in enumerate(a)}
        ia = [0] * n
        for idx, num in enumerate(a):
            ia[num-1] = idx  # since a contains 1-based numbers

        # Convert b to 0-based indices in b list
        b_zero = [num-1 for num in b]  # to 0-based internally

        ans = [float('inf')] * n
        # Priority queues store (-distance, original index)
        pq_left = []  # elements where i <= ia[b[i]]
        pq_right = []  # elements where i > ia[b[i]]

        for i in range(n):
            current_b = b_zero[i]
            pos_in_a = ia[current_b]
            diff = i - pos_in_a
            if i <= pos_in_a:
                heappush(pq_left, (-(pos_in_a - i), i))
            else:
                heappush(pq_right, (-(i - pos_in_a), i))
            ans[0] = min(ans[0], abs(i - pos_in_a))

        for k in range(1, n):
            # Move elements from previous shift out of the window
            prev_idx = k - 1
            current_b_prev = b_zero[prev_idx]
            pos_in_a_prev = ia[current_b_prev]
            shifted_pos = (prev_idx - (k-1)) % n  # was considered for previous k-1 shifts

            new_diff_for_next = (n - pos_in_a_prev - 1) + k
            heappush(pq_right, (-new_diff_for_next, n + prev_idx))

            # Remove elements from pq_right that are now in pq_left due to shift
            while pq_right and -pq_right[0][0] - k < 0:
                dist, idx = heappop(pq_right)
                new_dist = - (-dist - k)
                heappush(pq_left, (-new_dist, idx))

            # Remove elements from pq_left that are out of the valid indices (>=k)
            while pq_left and pq_left[0][1] < k:
                heappop(pq_left)

            current_min = float('inf')
            if pq_left:
                current_min = min(current_min, -pq_left[0][0] + k)
            if pq_right:
                current_min = min(current_min, -pq_right[0][0] - k)

            ans[k] = current_min

        return ans
