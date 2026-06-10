import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cfancynumber.Cfancynumber_reward_calculator import CfancynumberRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve_beautiful_number(n, k, original_number):
    s = list(original_number)
    c = [0] * 10
    for i in range(n):
        digit = int(s[i])
        c[digit] += 1

    def choosevalue(m):
        nonlocal c, n, k, s
        if c[m] >= k:
            return (0, original_number)
        p = s.copy()
        total_cost = 0
        remain = k - c[m]
        for i in range(1, 10):
            R = m + i
            L = m - i
            # Process R direction (higher digits)
            if R <= 9 and remain > 0:
                for j in range(n):
                    if remain <= 0:
                        break
                    if int(p[j]) == R:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            # Process L direction (lower digits)
            if L >= 0 and remain > 0:
                for j in range(n-1, -1, -1):
                    if remain <= 0:
                        break
                    if int(p[j]) == L:
                        p[j] = str(m)
                        total_cost += i
                        remain -= 1
            if remain <= 0:
                break
        new_number = ''.join(p)
        return (total_cost, new_number)

    best_cost = float('inf')
    best_number = None
    for m in range(10):
        current_cost, current_number = choosevalue(m)
        if current_cost < best_cost:
            best_cost = current_cost
            best_number = current_number
        elif current_cost == best_cost:
            if current_number < best_number:
                best_number = current_number
    return (best_cost, best_number)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CfancynumberVerificationTool(BaseTool):
    """Cfancynumber验证工具"""
    
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
            score = CfancynumberRewardCalculator.verify_score(
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
            logger.error(f"CfancynumberVerificationTool执行错误: {str(e)}")
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

