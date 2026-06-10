import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.enewyearandentityenumeration.Enewyearandentityenumeration_reward_calculator import EnewyearandentityenumerationRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局变量 ===

mod = 10**9 + 7

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EnewyearandentityenumerationVerificationTool(BaseTool):
    """Enewyearandentityenumeration验证工具"""
    
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
            score = EnewyearandentityenumerationRewardCalculator.verify_score(
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
            logger.error(f"EnewyearandentityenumerationVerificationTool执行错误: {str(e)}")
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
    def _generate_binary_strings(m, n):
        binaries = set()
        while len(binaries) < n:
            num = random.randint(0, (1 << m) - 1)
            binary = bin(num)[2:].zfill(m)
            binaries.add(binary)
        return list(binaries)

    @staticmethod
    def _Blist(m_val):
        A = [0] * m_val
        A[0] = 1
        R = [1, 1]
        for n in range(1, m_val):
            A[n] = A[0]
            for k in range(n, 0, -1):
                A[k-1] += A[k]
                A[k-1] %= mod
            R.append(A[0])
        return R

    @staticmethod
    def _compute_answer(m, T):
        n = len(T)
        t = [list(s) for s in T]
        ti = [int(''.join(row[k] for row in t), 2) for k in range(m)]
        left = set(range(m))
        gps = []
        while left:
            k = next(iter(left))
            current = ti[k]
            group = {j for j in left if ti[j] == current}
            left -= group
            gps.append(len(group))
        bell_numbers = Enewyearandentityenumerationbootcamp._Blist(m)
        res = 1
        for size in gps:
            res = res * bell_numbers[size] % mod
        return res
