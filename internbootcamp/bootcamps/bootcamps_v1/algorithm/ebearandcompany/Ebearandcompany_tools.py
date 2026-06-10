import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ebearandcompany.Ebearandcompany_reward_calculator import EbearandcompanyRewardCalculator

# 导入依赖库
import random
import string
from collections import defaultdict
import re

# === 源文件中的全局函数 ===

def compute_min_swaps(n, s):
    a, b, c = [], [], []
    for i in range(n):
        char = s[i]
        if char == 'V':
            a.append(i)
        elif char == 'K':
            b.append(i)
        else:
            c.append(i)
    
    def count(arr, st, x):
        ret = 0
        i = st
        while i < len(arr) and arr[i] < x:
            ret += 1
            i += 1
        return ret
    
    dp = defaultdict(lambda: float('inf'))
    dp[(0, 0, 0, 0)] = 0
    
    for i in range(len(a)+1):
        for j in range(len(b)+1):
            for k in range(len(c)+1):
                for p in range(2):
                    current_key = (i, j, k, p)
                    current_val = dp[current_key]
                    if current_val == float('inf'):
                        continue
                    
                    # Place V
                    if i < len(a):
                        cost = count(a, i, a[i]) + count(b, j, a[i]) + count(c, k, a[i])
                        new_key = (i+1, j, k, 1)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place K (only if previous was not V)
                    if j < len(b) and p == 0:
                        cost = count(a, i, b[j]) + count(b, j, b[j]) + count(c, k, b[j])
                        new_key = (i, j+1, k, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
                    
                    # Place other characters
                    if k < len(c):
                        cost = count(a, i, c[k]) + count(b, j, c[k]) + count(c, k, c[k])
                        new_key = (i, j, k+1, 0)
                        dp[new_key] = min(dp[new_key], current_val + cost)
    
    return min(dp[(len(a), len(b), len(c), 0)], dp[(len(a), len(b), len(c), 1)])

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EbearandcompanyVerificationTool(BaseTool):
    """Ebearandcompany验证工具"""
    
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
            score = EbearandcompanyRewardCalculator.verify_score(
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
            logger.error(f"EbearandcompanyVerificationTool执行错误: {str(e)}")
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

