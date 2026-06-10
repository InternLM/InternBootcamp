import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cworldeaterbrothers.Cworldeaterbrothers_reward_calculator import CworldeaterbrothersRewardCalculator

# 导入依赖库
import random
import re
import sys



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CworldeaterbrothersVerificationTool(BaseTool):
    """Cworldeaterbrothers验证工具"""
    
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
            score = CworldeaterbrothersRewardCalculator.verify_score(
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
            logger.error(f"CworldeaterbrothersVerificationTool执行错误: {str(e)}")
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
    def generate_tree(n):
        if n == 1:
            return []
        parents = [random.randint(0, i-1) for i in range(1, n)]
        edges = []
        for i in range(1, n):
            parent = parents[i-1]
            edges.append((parent, i))
        return edges

    @staticmethod
    def compute_answer(n, adj):
        if n == 1:
            return 0

        dp = [0] * n
        ans = n - 1

        def dfs1(v, p):
            for u, f in adj[v]:
                if u == p:
                    continue
                dfs1(u, v)
                dp[v] += dp[u] + (1 - f)

        dfs1(0, -1)

        def dfs2(v, p):
            for u, f in adj[v]:
                if u == p:
                    continue
                dp[u] = dp[v] + (1 if f else -1)
                dfs2(u, v)

        dfs2(0, -1)

        def dfs3(v, p):
            m1, m2 = 0, 0
            for u, f in adj[v]:
                if u == p:
                    continue
                cm1, cm2 = dfs3(u, v)
                current = cm1 + (0 if f else 1)
                if current >= m1:
                    m2 = m1
                    m1 = current
                elif current > m2:
                    m2 = current
            return (m1, m2)

        for i in range(n):
            mx1, mx2 = dfs3(i, -1)
            current_ans = dp[i] - mx1 - mx2
            ans = min(ans, current_ans)

        return ans
