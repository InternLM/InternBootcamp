import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccointroubles.Ccointroubles_reward_calculator import CcointroublesRewardCalculator

# 导入依赖库
import random
from collections import deque
import re

# === 源文件中的全局变量 ===

MOD = 10**9 + 7



# === 源文件中的全局函数 ===

def solve(n, q, t, a_list, constraints):
    """完整实现的解题算法"""
    # 初始化图结构
    g = [[] for _ in range(n+1)]
    in_degree = [0]*(n+1)
    for u, v in constraints:
        g[u].append(v)
        in_degree[v] += 1

    # 拓扑排序检测环
    queue = deque()
    topo_order = []
    for u in range(1, n+1):
        if in_degree[u] == 0:
            queue.append(u)
    
    while queue:
        u = queue.popleft()
        topo_order.append(u)
        for v in g[u]:
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)
    
    if len(topo_order) != n:
        return 0  # 存在环

    # 计算依赖关系和最小金额
    dep = [0]*(n+1)
    sum_ = [0]*(n+1)
    for u in reversed(topo_order):
        sum_[u] = a_list[u-1]
        max_child_dep = 0
        for v in g[u]:
            sum_[u] += sum_[v]
            if dep[v] > max_child_dep:
                max_child_dep = dep[v]
        dep[u] = max_child_dep + 1

    min_t = sum(a_list[u-1] * dep[u] for u in topo_order)
    if t < min_t:
        return 0

    # 动态规划计算组合数
    target = t - min_t
    dp = [0]*(target+1)
    dp[0] = 1
    for u in topo_order:
        s = sum_[u]
        for j in range(s, target+1):
            dp[j] = (dp[j] + dp[j - s]) % MOD
    
    return dp[target] % MOD if target >=0 else 0

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcointroublesVerificationTool(BaseTool):
    """Ccointroubles验证工具"""
    
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
            score = CcointroublesRewardCalculator.verify_score(
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
            logger.error(f"CcointroublesVerificationTool执行错误: {str(e)}")
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
    def _calculate_min_t(self, n, a, constraints):
        """辅助函数：计算最小金额"""
        try:
            temp_g = [[] for _ in range(n+1)]
            for u, v in constraints:
                temp_g[u].append(v)

            # 计算拓扑深度
            depth = [0]*(n+1)
            for u in range(n, 0, -1):
                max_child = 0
                for v in temp_g[u]:
                    max_child = max(max_child, depth[v])
                depth[u] = max_child + 1

            return sum(a[u-1] * depth[u] for u in range(1, n+1))
        except:
            return None
