import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.dbeautifulpairsofnumbers.Dbeautifulpairsofnumbers_reward_calculator import DbeautifulpairsofnumbersRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DbeautifulpairsofnumbersVerificationTool(BaseTool):
    """Dbeautifulpairsofnumbers验证工具"""
    
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
            score = DbeautifulpairsofnumbersRewardCalculator.verify_score(
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
            logger.error(f"DbeautifulpairsofnumbersVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def initialize_data(cls):
        if cls.initialized:
            return
        # Precompute factorial and inverse factorial arrays
        cls.fac = [1] * cls.maxn
        for i in range(1, cls.maxn):
            cls.fac[i] = cls.fac[i-1] * i % cls.mod

        cls.ifac = [1] * cls.maxn
        cls.ifac[cls.maxn - 1] = pow(cls.fac[cls.maxn - 1], cls.mod - 2, cls.mod)
        for i in range(cls.maxn - 2, -1, -1):
            cls.ifac[i] = cls.ifac[i + 1] * (i + 1) % cls.mod

        # Precompute s array
        cls.s = [0] * cls.maxn
        for i in range(1, cls.maxn):
            cls.s[i] = cls.s[i-1] + i

        # Initialize f array using dynamic programming
        cls.f = [[0] * cls.maxn for _ in range(cls.maxn)]
        for i in range(1, cls.maxn):
            cls.f[i][1] = 1

        for j in range(2, cls.maxn):
            if cls.s[j] >= cls.maxn:
                break
            if cls.s[j] < cls.maxn:
                cls.f[cls.s[j]][j] = cls.fac[j] % cls.mod
            for i in range(cls.s[j] + 1, cls.maxn):
                prev_i = i - j
                if prev_i >= 0:
                    term1 = cls.f[prev_i][j]
                    term2 = (cls.f[prev_i][j-1] * j) % cls.mod
                    cls.f[i][j] = (term1 + term2) % cls.mod

        cls.initialized = True

    @classmethod
    def compute_answer(cls, n, k):
        if k < 1 or k > n:
            return 0
        new_n = n - 1
        res = 0
        s_k_1 = cls.s[k-1]
        for i in range(s_k_1, new_n + 1):
            t = new_n - i - (k - 1)
            if t < 0:
                break
            comb = cls.C(k + t, t)
            if (i + k) >= cls.maxn or k >= cls.maxn:
                f_val = 0
            else:
                f_val = cls.f[i + k][k]
            res = (res + f_val * comb) % cls.mod
        return res

    @classmethod
    def C(cls, n, m):
        if m < 0 or m > n:
            return 0
        return cls.fac[n] * cls.ifac[m] % cls.mod * cls.ifac[n - m] % cls.mod
