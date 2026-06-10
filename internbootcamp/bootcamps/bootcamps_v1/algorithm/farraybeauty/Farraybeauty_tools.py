import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.farraybeauty.Farraybeauty_reward_calculator import FarraybeautyRewardCalculator

# 导入依赖库
import random
import re
from bisect import bisect_right

# === 源文件中的全局变量 ===

MOD = 998244353

INF = 10**18

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class FarraybeautyVerificationTool(BaseTool):
    """Farraybeauty验证工具"""
    
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
            score = FarraybeautyRewardCalculator.verify_score(
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
            logger.error(f"FarraybeautyVerificationTool执行错误: {str(e)}")
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
    def compute_answer(n, k, original_a):
        """优化后的计算逻辑，添加了提前终止条件和范围优化"""
        if k < 2:
            return 0

        sorted_a = sorted(original_a)
        max_diff = sorted_a[-1] - sorted_a[0]
        max_x = max_diff // (k-1) if k > 1 else 0

        # 调整循环范围为实际可能的最小值
        M = min(10**5 + 5, max_x + 2) if max_x else 10**5 + 5
        a = [-INF] + sorted_a
        ans = 0

        for x in range(1, M + 1):
            if x * (k-1) > M:
                break

            # 预处理指针数组
            l = [0]*(n+1)
            for i in range(1, n+1):
                target = a[i] - x
                l[i] = bisect_right(a, target, 0, i) - 1
                l[i] = max(l[i], l[i-1])

            # 动态规划部分
            dp = [[0]*(n+1) for _ in range(k+1)]
            dp[0][0] = 1

            for i in range(k):
                prefix = [0]*(n+1)
                prefix[0] = dp[i][0]
                for j in range(1, n+1):
                    prefix[j] = (prefix[j-1] + dp[i][j]) % MOD

                for j in range(1, n+1):
                    if l[j] >= 0:
                        dp[i+1][j] = prefix[l[j]] % MOD

            res = sum(dp[k][j] for j in range(1, n+1)) % MOD
            ans = (ans + res) % MOD

        return ans
