import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eprairiepartition.Eprairiepartition_reward_calculator import EprairiepartitionRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import bisect

# === 源文件中的全局函数 ===

def compute_possible_m(a):
    cnt1 = a.count(1)
    n = len(a)
    a_sorted = sorted(a)
    freq = defaultdict(int)
    for num in a_sorted:
        freq[num] += 1

    def is_possible(m):
        current_freq = freq.copy()

        if current_freq.get(1, 0) < m:
            return False
        current_freq[1] -= m

        last = [1] * m
        current_power = 2
        cnt = m

        while current_freq.get(current_power, 0) > 0 and cnt > 0:
            available = current_freq[current_power]
            take = min(available, cnt)
            current_freq[current_power] -= take
            for i in range(take):
                last[i] = current_power
            cnt = take
            current_power *= 2

        last_sorted = sorted(last)
        remaining = []
        for num, count in sorted(current_freq.items()):
            if count > 0:
                remaining.extend([num] * count)

        for num in remaining:
            required = (num + 1) // 2
            idx = bisect.bisect_left(last_sorted, required)
            if idx >= len(last_sorted):
                return False
            del last_sorted[idx]
            bisect.insort(last_sorted, num)

        return True

    left, right = 0, cnt1 + 1
    while left < right - 1:
        mid = (left + right) // 2
        if is_possible(mid):
            right = mid
        else:
            left = mid
    mi = right

    if mi > cnt1:
        return [-1]
    return list(range(mi, cnt1 + 1))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EprairiepartitionVerificationTool(BaseTool):
    """Eprairiepartition验证工具"""
    
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
            score = EprairiepartitionRewardCalculator.verify_score(
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
            logger.error(f"EprairiepartitionVerificationTool执行错误: {str(e)}")
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

