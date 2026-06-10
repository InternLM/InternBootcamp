import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.e1twilightandancientscrolleasierversion.E1twilightandancientscrolleasierversion_reward_calculator import E1twilightandancientscrolleasierversionRewardCalculator

# 导入依赖库
import re
import random
import bisect

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, words):
    if n == 0:
        return 0
    preprocessed = []
    for s in words:
        m = len(s)
        deletions = [s[:i] + s[i+1:] for i in range(m)]
        deletions.sort()
        preprocessed.append(deletions)
    
    prev_deletions = preprocessed[0]
    prev_prefix_sum = [0] * (len(prev_deletions) + 1)
    for i in range(len(prev_deletions)):
        prev_prefix_sum[i+1] = (prev_prefix_sum[i] + 1) % MOD
    
    for x in range(1, n):
        current_deletions = preprocessed[x]
        current_dp = []
        for s in current_deletions:
            j = bisect.bisect_right(prev_deletions, s)
            current_count = prev_prefix_sum[j]
            current_dp.append(current_count % MOD)
        
        current_prefix_sum = [0]
        current_sum = 0
        for cnt in current_dp:
            current_sum = (current_sum + cnt) % MOD
            current_prefix_sum.append(current_sum)
        
        prev_deletions = current_deletions
        prev_prefix_sum = current_prefix_sum
    
    return prev_prefix_sum[-1] % MOD

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class E1twilightandancientscrolleasierversionVerificationTool(BaseTool):
    """E1twilightandancientscrolleasierversion验证工具"""
    
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
            score = E1twilightandancientscrolleasierversionRewardCalculator.verify_score(
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
            logger.error(f"E1twilightandancientscrolleasierversionVerificationTool执行错误: {str(e)}")
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

