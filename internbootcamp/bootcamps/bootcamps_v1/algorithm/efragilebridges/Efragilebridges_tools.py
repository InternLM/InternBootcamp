import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.efragilebridges.Efragilebridges_reward_calculator import EfragilebridgesRewardCalculator

# 导入依赖库
import re
import random

# === 源文件中的全局函数 ===

def solve(n_platforms, a):
    """动态规划解法，包含完整边界校验"""
    if n_platforms < 2:
        return 0
    if len(a) != n_platforms - 1:
        raise ValueError("Bridge count mismatch")
    
    n = n_platforms - 1
    x = a.copy()
    
    # 右侧DP初始化
    r = [[0, 0] for _ in range(n_platforms)]
    for i in range(n-1, -1, -1):
        # 计算r[i][1]
        if x[i] == 1:
            r[i][1] = 0
        else:
            next_i = i + 1
            r_next_1 = r[next_i][1] if next_i < n_platforms else 0
            sum_val = r_next_1 + x[i]
            r[i][1] = sum_val & (~1)
        
        # 计算r[i][0]
        next_i = i + 1
        r_next_0 = r[next_i][0] if next_i < n_platforms else 0
        if x[i] % 2 == 1:
            r[i][0] = max(r[i][1], x[i] + r_next_0)
        else:
            r[i][0] = max(r[i][1], (x[i]-1) + r_next_0)
    
    # 左侧DP初始化
    l = [[0, 0] for _ in range(n_platforms)]
    for i in range(1, n_platforms):
        bridge_idx = i-1
        if bridge_idx < 0:
            continue
            
        x_val = x[bridge_idx]
        # 计算l[i][1]
        if x_val == 1:
            l[i][1] = 0
        else:
            prev_i = i-1
            l_prev_1 = l[prev_i][1] if prev_i >= 0 else 0
            sum_val = l_prev_1 + x_val
            l[i][1] = sum_val & (~1)
        
        # 计算l[i][0]
        prev_i = i-1
        l_prev_0 = l[prev_i][0] if prev_i >= 0 else 0
        if x_val % 2 == 1:
            l[i][0] = max(l[i][1], x_val + l_prev_0)
        else:
            l[i][0] = max(l[i][1], (x_val-1) + l_prev_0)
    
    # 计算最大值
    max_score = 0
    for i in range(n_platforms):
        current = r[i][0] + l[i][0]
        max_score = max(max_score, current)
    return max_score

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EfragilebridgesVerificationTool(BaseTool):
    """Efragilebridges验证工具"""
    
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
            score = EfragilebridgesRewardCalculator.verify_score(
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
            logger.error(f"EfragilebridgesVerificationTool执行错误: {str(e)}")
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

