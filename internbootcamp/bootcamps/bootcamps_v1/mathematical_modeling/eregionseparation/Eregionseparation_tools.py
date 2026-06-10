import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.eregionseparation.Eregionseparation_reward_calculator import EregionseparationRewardCalculator

# 导入依赖库
import math
import random

# === 源文件中的全局变量 ===

MOD = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EregionseparationVerificationTool(BaseTool):
    """Eregionseparation验证工具"""
    
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
            score = EregionseparationRewardCalculator.verify_score(
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
            logger.error(f"EregionseparationVerificationTool执行错误: {str(e)}")
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
    def _compute_answer(n, a_list, p_list):
        """动态计算正确答案"""
        if n == 0:
            return 0

        # 初始化数据结构
        a = [0] * (n + 1)
        for i in range(n):
            a[i+1] = a_list[i]

        # 构建父节点数组
        fa = [0] * (n + 1)
        for idx, parent in enumerate(p_list):
            fa[idx+2] = parent  # p_list对应城市2到n的父节点

        # 自底向上计算子树和
        for i in range(n, 1, -1):
            a[fa[i]] += a[i]

        S = a[1]
        if S == 0:
            return 0

        # 处理a数组
        for i in range(1, n+1):
            a[i] = S // math.gcd(S, a[i])

        # 计算频率数组
        freq = [0] * (n + 2)
        for i in range(1, n+1):
            if a[i] <= n:
                freq[a[i]] += 1

        # 因数叠加
        for i in range(n, 0, -1):
            j = 2 * i
            while j <= n:
                freq[j] += freq[i]
                j += i

        # 动态规划求解
        dp = [0] * (n + 2)
        dp[1] = 1
        ans = 0
        for i in range(1, n+1):
            if freq[i] == i:
                ans = (ans + dp[i]) % MOD
                j = 2 * i
                while j <= n:
                    dp[j] = (dp[j] + dp[i]) % MOD
                    j += i

        return ans % MOD
