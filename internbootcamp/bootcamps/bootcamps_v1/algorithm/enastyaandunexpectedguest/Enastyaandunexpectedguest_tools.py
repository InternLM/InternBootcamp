import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.enastyaandunexpectedguest.Enastyaandunexpectedguest_reward_calculator import EnastyaandunexpectedguestRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def correct_solution(n, m, d, g, r):
    d_sorted = sorted(d)
    # Check if any adjacent islands exceed g distance
    for i in range(1, len(d_sorted)):
        if d_sorted[i] - d_sorted[i-1] > g:
            return -1
    m = len(d_sorted)
    INF = float('inf')
    dp = [[INF] * (g + 1) for _ in range(m)]
    dp[0][0] = 0
    heap = []
    import heapq
    heapq.heappush(heap, (0, 0, 0))  # (cycles, u, rem)

    while heap:
        cycles, u, rem = heapq.heappop(heap)
        if cycles > dp[u][rem]:
            continue
        for dv in [-1, 1]:
            v = u + dv
            if 0 <= v < m:
                distance = abs(d_sorted[u] - d_sorted[v])
                new_rem = rem + distance
                if new_rem > g:
                    continue
                if new_rem == g:
                    new_cycles = cycles + 1
                    new_r = 0
                else:
                    new_cycles = cycles
                    new_r = new_rem
                if dp[v][new_r] > new_cycles:
                    dp[v][new_r] = new_cycles
                    heapq.heappush(heap, (new_cycles, v, new_r))
    min_time = INF
    for i in range(m):
        time_needed = n - d_sorted[i]
        if time_needed <= g and dp[i][0] != INF:
            total_time = dp[i][0] * (g + r) + time_needed
            if total_time < min_time:
                min_time = total_time
    return min_time if min_time != INF else -1

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EnastyaandunexpectedguestVerificationTool(BaseTool):
    """Enastyaandunexpectedguest验证工具"""
    
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
            score = EnastyaandunexpectedguestRewardCalculator.verify_score(
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
            logger.error(f"EnastyaandunexpectedguestVerificationTool执行错误: {str(e)}")
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

