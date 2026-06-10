import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.enumbertransformation.Enumbertransformation_reward_calculator import EnumbertransformationRewardCalculator

# 导入依赖库
import random
import re
import math

# === 源文件中的全局函数 ===

def lcm(a, b):
    return a * b // math.gcd(a, b)

def compute_mod(k):
    mod = 1
    for x in range(2, k+1):
        mod = lcm(mod, x)
    return mod

def dynamic_get(r1, r2, k):
    x_list = list(range(2, k+1))
    max_r = r2
    d = [float('inf')] * (max_r + 1)
    d[r1] = 0

    current_mods = [r1 % x for x in x_list]

    for i in range(r1 + 1, r2 + 1):
        new_mods = []
        min_steps = d[i-1] + 1
        for idx, x in enumerate(x_list):
            new_mod = current_mods[idx] + 1
            if new_mod >= x:
                new_mod = 0
            new_mods.append(new_mod)
            if new_mod != 0 and i - new_mod >= r1:
                candidate = d[i - new_mod] + 1
                if candidate < min_steps:
                    min_steps = candidate
        current_mods = new_mods
        d[i] = min_steps
    return d[r2]

def solve(a, b, k):
    if a == b:
        return 0
    mod = compute_mod(k)
    ra = a % mod
    rb = b % mod

    if a - b < mod and ra >= rb:
        return dynamic_get(rb, ra, k)
    else:
        part1 = dynamic_get(rb, mod - 1, k) + 1  # 上升到模的倍数
        part2 = dynamic_get(0, ra, k)
        cycle_num = (a - ra - (b - rb + mod)) // mod
        part3 = (dynamic_get(0, mod-1, k) + 1) * cycle_num
        return part1 + part2 + part3

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EnumbertransformationVerificationTool(BaseTool):
    """Enumbertransformation验证工具"""
    
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
            score = EnumbertransformationRewardCalculator.verify_score(
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
            logger.error(f"EnumbertransformationVerificationTool执行错误: {str(e)}")
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

