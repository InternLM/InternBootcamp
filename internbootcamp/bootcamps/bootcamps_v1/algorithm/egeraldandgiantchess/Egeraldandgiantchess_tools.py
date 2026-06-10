import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.egeraldandgiantchess.Egeraldandgiantchess_reward_calculator import EgeraldandgiantchessRewardCalculator

# 导入依赖库
import re

# === 源文件中的全局变量 ===

global_fac = [1]

global_inv = [1]

mod_value = 10**9 + 7



# === 源文件中的全局函数 ===

def init_global_fac_inv(maxn):
    global global_fac, global_inv, mod_value
    if maxn < len(global_fac):
        return
    current_len = len(global_fac)
    for i in range(current_len, maxn + 1):
        global_fac.append((global_fac[-1] * i) % mod_value)
        inv_i = pow(i, mod_value - 2, mod_value)
        new_inv = (global_inv[-1] * inv_i) % mod_value
        global_inv.append(new_inv)

def culC(a, b):
    if a < 0 or b < 0 or a < b:
        return 0
    init_global_fac_inv(a)
    return global_fac[a] * global_inv[b] % mod_value * global_inv[a - b] % mod_value

def path(sx, sy, tx, ty):
    dx = tx - sx
    dy = ty - sy
    if dx < 0 or dy < 0:
        return 0
    return culC(dx + dy, dx)

def compute_solution(h, w, blocks):
    mod = 10**9 + 7
    blocks_sorted = sorted(blocks, key=lambda x: (x[0], x[1]))
    blocks_sorted.append((h, w))
    n = len(blocks_sorted)
    dp = [0] * n

    for i in range(n):
        r, c = blocks_sorted[i]
        total = path(1, 1, r, c)
        for j in range(i):
            pr, pc = blocks_sorted[j]
            if pr <= r and pc <= c:
                ways = path(pr, pc, r, c) * dp[j]
                total = (total - ways) % mod
        dp[i] = total % mod
    return dp[-1]

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EgeraldandgiantchessVerificationTool(BaseTool):
    """Egeraldandgiantchess验证工具"""
    
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
            score = EgeraldandgiantchessRewardCalculator.verify_score(
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
            logger.error(f"EgeraldandgiantchessVerificationTool执行错误: {str(e)}")
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

