import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.earrangement.Earrangement_reward_calculator import EarrangementRewardCalculator

# 导入依赖库
import re
import random
from collections import deque

# === 源文件中的全局函数 ===

def is_dag(edges, n_nodes):
    adj = [[] for _ in range(n_nodes + 1)]
    in_degree = [0] * (n_nodes + 1)
    for u, v in edges:
        adj[u].append(v)
        in_degree[v] += 1
    queue = deque()
    for node in range(1, n_nodes + 1):
        if in_degree[node] == 0:
            queue.append(node)
    visited = 0
    while queue:
        u = queue.popleft()
        visited += 1
        for v in adj[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    return visited == n_nodes

def calculate_count(n, ls, pref):
    dp = [0] * (1 << n)
    dp[0] = 1
    for mask in range(1 << n):
        if dp[mask] == 0:
            continue
        cnt = bin(mask).count('1')
        for i in range(n):
            if pref[i] != -1 and pref[i] != (n - cnt - 1):
                continue
            if (ls[i] & mask) != ls[i]:
                continue
            if (mask & (1 << i)) != 0:
                continue
            new_mask = mask | (1 << i)
            dp[new_mask] += dp[mask]
    return dp[(1 << n) - 1]

def solve_puzzle(n, y, m, constraints):
    original_y = y
    y -= 2000
    if y <= 0:
        return "The times have changed"
    ls = [0] * n
    for u, v in constraints:
        ai = u - 1
        bi_seat = v - 1
        ls[ai] |= 1 << bi_seat
    pref = [-1] * n
    for i in range(n):
        while True:
            pref[i] += 1
            if pref[i] >= n:
                return "The times have changed"
            current_pref = pref[:i+1] + [-1] * (n - i - 1)
            current_count = calculate_count(n, ls, current_pref)
            if current_count < y:
                y -= current_count
            else:
                break
    arrangement = [str(p + 1) for p in pref]
    return ' '.join(arrangement)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EarrangementVerificationTool(BaseTool):
    """Earrangement验证工具"""
    
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
            score = EarrangementRewardCalculator.verify_score(
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
            logger.error(f"EarrangementVerificationTool执行错误: {str(e)}")
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

