import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dratingcompression.Dratingcompression_reward_calculator import DratingcompressionRewardCalculator

# 导入依赖库
import random
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DratingcompressionVerificationTool(BaseTool):
    """Dratingcompression验证工具"""
    
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
            score = DratingcompressionRewardCalculator.verify_score(
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
            logger.error(f"DratingcompressionVerificationTool执行错误: {str(e)}")
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
    def optimized_solve(self, n, a):
        """准确高效的解法实现"""
        answer = ['0'] * n

        # 预处理k=1的情况
        k1_valid = (sorted(a) == list(range(1, n+1)))
        answer[0] = '1' if k1_valid else '0'

        # 预处理每个位置的next smaller元素
        next_smaller = [n] * n
        prev_smaller = [-1] * n
        stack = []

        for i in range(n):
            while stack and a[i] < a[stack[-1]]:
                next_smaller[stack.pop()] = i
            prev_smaller[i] = stack[-1] if stack else -1
            stack.append(i)

        # 统计每个元素作为最小值的影响范围
        min_intervals = {}
        for i in range(n):
            left = prev_smaller[i] + 1
            right = next_smaller[i] - 1
            min_intervals[a[i]] = max(min_intervals.get(a[i], 0), right - left + 1)

        # 根据定理：当且仅当存在元素只能在窗口大小>=某个值时出现
        for m in range(1, n):
            max_k = n - m + 1
            if m in min_intervals and min_intervals[m] >= m:
                for k in range(max(1, m), max_k+1):
                    if k <= min_intervals[m]:
                        answer[k-1] = '1'

        # 最终验证每个k的结果
        for k in range(1, n+1):
            m = n - k + 1
            if m < 1:
                continue
            if answer[k-1] == '1':
                # 二次验证确保正确性
                window_min = self.sliding_window_min(a, k)
                if not self.is_permutation(window_min, m):
                    answer[k-1] = '0'
        return ''.join(answer)

    @staticmethod
    def sliding_window_min(arr, k):
        """精确计算滑动窗口的最小值"""
        dq = deque()
        result = []
        for i, num in enumerate(arr):
            while dq and arr[dq[-1]] >= num:
                dq.pop()
            dq.append(i)

            if dq[0] == i - k:
                dq.popleft()

            if i >= k - 1:
                result.append(arr[dq[0]])
        return result

    @staticmethod
    def is_permutation(nums, m):
        """验证是否为1~m的排列"""
        return len(nums) == m and set(nums) == set(range(1, m+1)) and len(set(nums)) == m
