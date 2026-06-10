import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ethegreatmixing.Ethegreatmixing_reward_calculator import EthegreatmixingRewardCalculator

# 导入依赖库
import random
import re
from itertools import combinations

# === 源文件中的全局函数 ===

def solve_case(n, c):
    if n in c:
        return 1
    q = {cc - n for cc in c}
    max_q = max(q)
    min_q = min(q)
    if max_q < 0 or min_q > 0:
        return -1
    max_positive = max_q
    min_negative_abs = -min_q
    maxs = [3000] * (max_positive + 1)
    mins = [3000] * (min_negative_abs + 1)
    for qq in q:
        if qq > 0 and qq <= max_positive:
            maxs[qq] = 1
        elif qq < 0:
            idx = -qq
            if idx <= min_negative_abs:
                mins[idx] = 1
    ans = float('inf')
    mni = len(mins) - 1
    mxi = len(maxs) - 1
    while mni > 0 and mxi > 0:
        if mni > mxi:
            mni, mxi = mxi, mni
            mins, maxs = maxs, mins
        for i in range(mni, 0, -1):
            if mxi - i >= 0:
                maxs[mxi - i] = min(maxs[mxi - i], maxs[mxi] + mins[i])
        mxi -= 1
        while mxi > 0 and maxs[mxi] > 2500:
            mxi -= 1
    final_min = min(maxs[0], mins[0])
    return final_min if final_min <= 2500 else -1

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EthegreatmixingVerificationTool(BaseTool):
    """Ethegreatmixing验证工具"""
    
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
            score = EthegreatmixingRewardCalculator.verify_score(
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
            logger.error(f"EthegreatmixingVerificationTool执行错误: {str(e)}")
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

