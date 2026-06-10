import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.f1frequencyproblemeasyversion.F1frequencyproblemeasyversion_reward_calculator import F1frequencyproblemeasyversionRewardCalculator

# 导入依赖库
from collections import defaultdict
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class F1frequencyproblemeasyversionVerificationTool(BaseTool):
    """F1frequencyproblemeasyversion验证工具"""
    
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
            score = F1frequencyproblemeasyversionRewardCalculator.verify_score(
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
            logger.error(f"F1frequencyproblemeasyversionVerificationTool执行错误: {str(e)}")
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
    def _create_multi_max_case(self, n, val1, val2):
        """创建两个最高频次相同的案例"""
        k = random.randint(1, n//2)
        arr = [val1]*k + [val2]*k
        if n > 2*k:
            arr += random.choices([val1, val2], k=n-2*k)
        random.shuffle(arr)
        return {'array': arr, 'answer': n}

    def _create_single_max_case(self, n):
        """创建存在有效子数组的案例"""
        main_val = random.randint(1, self.max_val)
        sec_val = random.choice([x for x in range(1, self.max_val+1) if x != main_val])

        # 确保存在有效子数组
        arr = [main_val]*(n-2) + [sec_val]*2
        random.shuffle(arr)
        return {'array': arr, 'answer': self._optimized_solve(arr)}

    def _optimized_solve(self, array):
        """优化后的求解算法"""
        freq = defaultdict(int)
        for num in array:
            freq[num] += 1

        # 找出前两个最高频元素
        sorted_freq = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
        if len(sorted_freq) >= 2 and sorted_freq[0][1] == sorted_freq[1][1]:
            return len(array)

        if not sorted_freq:
            return 0

        # 仅考虑前两个可能候选元素
        main_val = sorted_freq[0][0]
        candidates = [item[0] for item in sorted_freq[1:min(5, len(sorted_freq))]]
        max_len = 0

        for candidate in candidates:
            current_len = self._find_length(array, main_val, candidate)
            max_len = max(max_len, current_len)

        return max_len if max_len > 0 else 0

    def _find_length(self, arr, val1, val2):
        """优化后的子数组查找算法"""
        prefix_sum = 0
        first_occurrence = {0: -1}
        max_len = 0

        for idx, num in enumerate(arr):
            if num == val1:
                prefix_sum += 1
            elif num == val2:
                prefix_sum -= 1

            if prefix_sum in first_occurrence:
                max_len = max(max_len, idx - first_occurrence[prefix_sum])
            else:
                first_occurrence[prefix_sum] = idx

        return max_len
