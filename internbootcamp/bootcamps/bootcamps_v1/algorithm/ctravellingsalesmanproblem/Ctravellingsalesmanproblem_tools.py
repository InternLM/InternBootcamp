import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ctravellingsalesmanproblem.Ctravellingsalesmanproblem_reward_calculator import CtravellingsalesmanproblemRewardCalculator

# 导入依赖库
from heapq import heappush
from heapq import heappop
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CtravellingsalesmanproblemVerificationTool(BaseTool):
    """Ctravellingsalesmanproblem验证工具"""
    
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
            score = CtravellingsalesmanproblemRewardCalculator.verify_score(
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
            logger.error(f"CtravellingsalesmanproblemVerificationTool执行错误: {str(e)}")
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
    def calculate_min_cost(n, a):
        a.sort()
        to = [0] * n
        d = [float('inf')] * n
        d[0] = 0
        q = [(0, 0)]
        total_c = sum(c for _, c in a)

        # 预计算每个城市的可达范围
        for i in range(n):
            x, y = a[i]
            l, r = i, n
            while l < r:
                m = (l + r) // 2
                if a[m][0] <= x + y:
                    l = m + 1
                else:
                    r = m
            to[i] = l - 1

        # 动态规划推进
        while q:
            cost, p = heappop(q)
            if cost > d[p]:
                continue

            # 向左扩展
            if p > 0 and d[p-1] > cost:
                d[p-1] = cost
                heappush(q, (cost, p-1))

            # 向右扩展
            if to[p] < n and d[to[p]] > cost:
                d[to[p]] = cost
                heappush(q, (cost, to[p]))

            # 跳跃扩展
            if to[p] + 1 < n:
                new_cost = cost + (a[to[p]+1][0] - a[p][0] - a[p][1])
                if new_cost < d[to[p]+1]:
                    d[to[p]+1] = new_cost
                    heappush(q, (new_cost, to[p]+1))

        return total_c + d[-1]
