import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dnewyearandancientprophecy.Dnewyearandancientprophecy_reward_calculator import DnewyearandancientprophecyRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def compute_answer(n, digits_str):
    if n == 0:
        return 0
    d = [int(c) for c in digits_str]
    if n == 1:
        return 1
    
    # Initialize comparison matrix
    comp = [[0]*(n+1) for _ in range(n)]
    
    for l in range(1, n):
        equal_count = 0
        for i in range(n - l):
            j = i + l
            if d[i] == d[j]:
                equal_count += 1
                if equal_count >= l:
                    equal_count = l - 1
            else:
                if d[i] < d[j]:
                    # Mark all positions in the equal prefix
                    start = i - equal_count
                    end = i + 1
                    for k in range(start, end):
                        if k >= 0 and j - equal_count + (k - start) < n:
                            comp[k][j - equal_count + (k - start) + 1] = 1
                equal_count = 0
    
    # Dynamic programming table
    dp = [[0]*(n+1) for _ in range(n+1)]
    for j in range(1, n+1):
        dp[j][j] = 1
    
    # Fill DP table
    for i in range(1, n):
        if d[i] == 0:
            continue
        prefix_sum = 0
        for l in range(1, n - i + 1):
            prefix_sum = (prefix_sum + dp[i][l-1]) % MOD
            if l <= i:
                compare_pos = i - l
                if compare_pos >= 0 and comp[compare_pos][i]:
                    dp[i+l][l] = (prefix_sum + dp[i][l]) % MOD
                else:
                    dp[i+l][l] = prefix_sum
            else:
                dp[i+l][l] = prefix_sum
    
    # Calculate final answer
    total = 0
    for l in range(1, n+1):
        total = (total + dp[n][l]) % MOD
    return total

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DnewyearandancientprophecyVerificationTool(BaseTool):
    """Dnewyearandancientprophecy验证工具"""
    
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
            score = DnewyearandancientprophecyRewardCalculator.verify_score(
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
            logger.error(f"DnewyearandancientprophecyVerificationTool执行错误: {str(e)}")
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

