import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ewatchingfireworksisfun.Ewatchingfireworksisfun_reward_calculator import EwatchingfireworksisfunRewardCalculator

# 导入依赖库
import random
import math

# === 源文件中的全局函数 ===

def build_sparse_table(arr, n):
    log_table = [0] * (n + 1)
    for i in range(2, n + 1):
        log_table[i] = log_table[i // 2] + 1
    k_max = log_table[n] + 1
    st = [[0] * (n + 1) for _ in range(k_max)]
    for i in range(1, n + 1):
        st[0][i] = arr[i]
    for j in range(1, k_max):
        for i in range(1, n + 1 - (1 << j) + 1):
            st[j][i] = min(st[j-1][i], st[j-1][i + (1 << (j-1))])
    return st, log_table

def query_min(st, log_table, l, r):
    length = r - l + 1
    k = log_table[length]
    return min(st[k][l], st[k][r - (1 << k) + 1])

def calculate_answer(n, m, d, fireworks):
    sum_bi = sum(b for a, b, t in fireworks)
    a_list = [a for a, b, t in fireworks]
    t_list = [t for a, b, t in fireworks]
    
    prev_dp = [0] * (n + 2)
    a1 = a_list[0]
    for j in range(1, n + 1):
        prev_dp[j] = abs(a1 - j)
    
    for i in range(1, m):
        ai = a_list[i]
        ti = t_list[i]
        delta_t = ti - t_list[i-1]
        tt = d * delta_t
        tt = min(tt, n)
        
        st, log_table = build_sparse_table(prev_dp, n)
        curr_dp = [0] * (n + 2)
        
        for j in range(1, n + 1):
            left = max(1, j - tt)
            right = min(n, j + tt)
            if left > right:
                curr_dp[j] = float('inf')
            else:
                min_prev = query_min(st, log_table, left, right)
                curr_dp[j] = min_prev + abs(ai - j)
        
        prev_dp, curr_dp = curr_dp, prev_dp
    
    min_final = min(prev_dp[j] for j in range(1, n + 1))
    return sum_bi - min_final

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EwatchingfireworksisfunVerificationTool(BaseTool):
    """Ewatchingfireworksisfun验证工具"""
    
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
            score = EwatchingfireworksisfunRewardCalculator.verify_score(
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
            logger.error(f"EwatchingfireworksisfunVerificationTool执行错误: {str(e)}")
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

