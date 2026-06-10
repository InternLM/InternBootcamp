import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cdoegraphs.Cdoegraphs_reward_calculator import CdoegraphsRewardCalculator

# 导入依赖库
import re
import random
from functools import lru_cache



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CdoegraphsVerificationTool(BaseTool):
    """Cdoegraphs验证工具"""
    
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
            score = CdoegraphsRewardCalculator.verify_score(
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
            logger.error(f"CdoegraphsVerificationTool执行错误: {str(e)}")
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
    def compute_doe_fib(n):
        """Generates the Fibonacci sequence for Doe graph sizes up to order n (0-based)."""
        if n < 0:
            return []
        fib = [1]  # D(0)
        if n == 0:
            return fib
        fib.append(2)  # D(1)
        for i in range(2, n + 1):
            fib.append(fib[i-1] + fib[i-2])
        return fib

    @classmethod
    def dfs(cls, a, b, k, fib_tuple):
        if a == b:
            return 0
        if k == 1:
            return 1
        if a > b:
            a, b = b, a
        return cls._dfs(a, b, k, fib_tuple)

    @classmethod
    def _dfs(cls, a, b, k, fib_tuple):
        if a == b:
            return 0
        if k == 1:
            return 1
        if k == 0:
            return 0

        size_k_1 = fib_tuple[k-1]
        if a > size_k_1 and b > size_k_1:
            return cls._dfs(a - size_k_1, b - size_k_1, k-2, fib_tuple)
        if a <= size_k_1 and b <= size_k_1:
            path_in = cls._dfs(a, b, k-1, fib_tuple)
            path1 = cls.dfs1(k-1, 0, a, fib_tuple) + cls.dfs2(k-1, 1, b, fib_tuple) + 2
            path2 = cls.dfs1(k-1, 1, a, fib_tuple) + cls.dfs2(k-1, 0, b, fib_tuple) + 2
            return min(path_in, path1, path2)
        else:
            path1 = min(cls.dfs1(k-1, 0, a, fib_tuple), cls.dfs1(k-1, 1, a, fib_tuple))
            path2 = cls.dfs2(k-2, 0, b - size_k_1, fib_tuple) + 1
            return path1 + path2

    @classmethod
    @lru_cache(maxsize=None)
    def dfs1(cls, a, b, c, fib_tuple):
        if a == 1:
            return 1 if (c + b) == 2 else 0
        if a == 0:
            return 0
        size_a_1 = fib_tuple[a-1]
        if b:
            if c > size_a_1:
                return cls.dfs1(a-2, 1, c - size_a_1, fib_tuple)
            else:
                option1 = cls.dfs1(a-1, 1, c, fib_tuple)
                option2 = cls.dfs1(a-1, 0, c, fib_tuple)
                return min(option1, option2) + 1 + (a-1) // 2
        else:
            if c > size_a_1:
                return cls.dfs1(a-2, 0, c - size_a_1, fib_tuple) + 1
            else:
                option1 = cls.dfs1(a-1, 0, c, fib_tuple)
                option2 = cls.dfs1(a-1, 1, c, fib_tuple) + 2
                return min(option1, option2)

    @classmethod
    @lru_cache(maxsize=None)
    def dfs2(cls, a, b, c, fib_tuple):
        if a == 1:
            return 1 if (c + b) == 2 else 0
        if a == 0:
            return 0
        size_a_1 = fib_tuple[a-1]
        if b:
            if c > size_a_1:
                return cls.dfs2(a-2, 1, c - size_a_1, fib_tuple)
            else:
                option1 = cls.dfs2(a-1, 1, c, fib_tuple)
                option2 = cls.dfs2(a-1, 0, c, fib_tuple)
                return min(option1, option2) + 1 + (a-1) // 2
        else:
            if c > size_a_1:
                return cls.dfs2(a-2, 0, c - size_a_1, fib_tuple) + 1
            else:
                option1 = cls.dfs2(a-1, 0, c, fib_tuple)
                option2 = cls.dfs2(a-1, 1, c, fib_tuple) + 2
                return min(option1, option2)
