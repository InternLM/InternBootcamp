import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clru.Clru_reward_calculator import ClruRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_expected_probabilities(n, k, p_list):
    non_zero = [(idx, p) for idx, p in enumerate(p_list) if p > 1e-9]
    cnt = len(non_zero)
    real_k = min(k, cnt)
    
    if real_k >= cnt:
        expected = [0.0] * n
        for idx, p in non_zero:
            expected[idx] = 1.0
        return expected
    
    s = 1 << cnt
    sum_state = [0.0] * s
    for state in range(s):
        total = 0.0
        for j in range(cnt):
            if state & (1 << j):
                total += non_zero[j][1]
        sum_state[state] = total
    
    f = [0.0] * s
    f[0] = 1.0
    
    for state in range(1, s):
        for j in range(cnt):
            if state & (1 << j):
                prev = state ^ (1 << j)
                denominator = 1.0 - sum_state[prev]
                if denominator < 1e-9:
                    continue
                f[state] += f[prev] * non_zero[j][1] / denominator
    
    expected = [0.0] * n
    for state in range(s):
        pc = bin(state).count('1')
        if pc == real_k:
            for j in range(cnt):
                if state & (1 << j):
                    idx = non_zero[j][0]
                    expected[idx] += f[state]
    
    return expected

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ClruVerificationTool(BaseTool):
    """Clru验证工具"""
    
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
            score = ClruRewardCalculator.verify_score(
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
            logger.error(f"ClruVerificationTool执行错误: {str(e)}")
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
    def is_close(a, b, rel_tol=1e-6, abs_tol=1e-6):
        return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)
