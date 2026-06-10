import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cjeremybearimy.Cjeremybearimy_reward_calculator import CjeremybearimyRewardCalculator

# 导入依赖库
from collections import defaultdict
from collections import deque
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CjeremybearimyVerificationTool(BaseTool):
    """Cjeremybearimy验证工具"""
    
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
            score = CjeremybearimyRewardCalculator.verify_score(
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
            logger.error(f"CjeremybearimyVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def calculate_GB(cls, k, edges):
        n = 2 * k
        adj = defaultdict(list)
        for u, v, t in edges:
            adj[u].append((v, t))
            adj[v].append((u, t))

        # BFS建立父子关系
        par = [0] * (n + 1)
        cst = [0] * (n + 1)
        q = deque([1])
        par[1] = -1  # 根节点无父

        while q:
            u = q.popleft()
            for v, t in adj[u]:
                if par[v] == 0 and v != par[u]:
                    par[v] = u
                    cst[v] = t
                    q.append(v)

        # 后序遍历计算子树大小
        dp = [1] * (n + 1)
        stack = []
        visited = [False] * (n + 1)
        stack.append((1, False))

        while stack:
            node, processed = stack.pop()
            if processed:
                for v, _ in adj[node]:
                    if v != par[node] and par[v] == node:
                        dp[node] += dp[v]
                continue
            if visited[node]:
                continue
            visited[node] = True
            stack.append((node, True))
            # 子节点逆序入栈保证处理顺序
            children = [v for v, _ in adj[node] if v != par[node] and par[v] == node]
            for child in reversed(children):
                stack.append((child, False))

        mn = mx = 0
        for v in range(2, n + 1):
            mn += cst[v] * (dp[v] % 2)
            mx += cst[v] * min(dp[v], n - dp[v])

        return mn, mx
