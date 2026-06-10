import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clevkoandstrings.Clevkoandstrings_reward_calculator import ClevkoandstringsRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ClevkoandstringsVerificationTool(BaseTool):
    """Clevkoandstrings验证工具"""
    
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
            score = ClevkoandstringsRewardCalculator.verify_score(
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
            logger.error(f"ClevkoandstringsVerificationTool执行错误: {str(e)}")
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
    def compute_answer(n, k, s):
        if k > n*(n+1)//2 or k < 0:
            return 0
        MAX_K = 2000
        k = min(k, MAX_K)

        dp = [[0]*(MAX_K+1) for _ in range(n+1)]
        sum1 = [0]*(MAX_K+1)
        dp[n][0] = 1

        for i in range(n-1, -1, -1):
            new_sum1 = [0]*(MAX_K+1)
            for j in range(MAX_K, -1, -1):
                current = 0

                # Case 1: t[i] < s[i]
                if j <= MAX_K:
                    current += (ord(s[i]) - ord('a')) * dp[i+1][j]

                # Case 2: t[i] > s[i]
                delta = n - i
                if delta <= j <= MAX_K:
                    current += (ord('z') - ord(s[i])) * dp[i+1][j - delta]

                # Case 3: Find first differing position
                used = [False]*(n+1)
                # 处理降序
                for l in range(n-1, i, -1):
                    used[l] = True
                    cnt = (n - l) * (l - i + 1)
                    if cnt > j:
                        break
                    rem = j - cnt
                    if 0 <= rem <= MAX_K:
                        current += (ord('z') - ord(s[l])) * dp[l+1][rem]

                # 处理升序
                for l in range(i+1, n):
                    if used[l]:
                        break
                    cnt = (n - l) * (l - i + 1)
                    if cnt > j:
                        break
                    rem = j - cnt
                    if 0 <= rem <= MAX_K:
                        current += (ord('z') - ord(s[l])) * dp[l+1][rem]

                # Add sum from previous steps
                current += sum1[j]
                if j == 0:
                    current += 1  # 全匹配的情况

                dp[i][j] = current % MOD
                # 更新sum1
                new_sum1[j] = (sum1[j] + (ord(s[i]) - ord('a')) * dp[i+1][j]) % MOD

            sum1 = new_sum1

        return dp[0][k] % MOD
