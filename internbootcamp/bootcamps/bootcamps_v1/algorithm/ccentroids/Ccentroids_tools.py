import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccentroids.Ccentroids_reward_calculator import CcentroidsRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcentroidsVerificationTool(BaseTool):
    """Ccentroids验证工具"""
    
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
            score = CcentroidsRewardCalculator.verify_score(
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
            logger.error(f"CcentroidsVerificationTool执行错误: {str(e)}")
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
    def generate_random_tree(n):
        if n == 1:
            return []
        edges = []
        for i in range(2, n+1):
            p = random.randint(1, i-1)
            edges.append((p, i))
        random.shuffle(edges)
        return edges

    @staticmethod
    def solve_problem(n, edges):
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        # 第一次DFS寻找重心
        siz = [0]*(n+1)
        res = float('inf')
        rt = 0
        def dfs1(x, F):
            nonlocal res, rt
            siz[x] = 1
            mx = 0
            for y in adj[x]:
                if y == F:
                    continue
                dfs1(y, x)
                siz[x] += siz[y]
                mx = max(mx, siz[y])
            mx = max(mx, n - siz[x])
            if mx < res or (mx == res and x < rt):
                res = mx
                rt = x
        dfs1(1, 0)

        # 第二次DFS建立父节点关系
        siz = [0]*(n+1)
        parent = {}
        def dfs2(x, F):
            parent[x] = F
            siz[x] = 1
            for y in adj[x]:
                if y == F:
                    continue
                dfs2(y, x)
                siz[x] += siz[y]
        dfs2(rt, 0)

        # 获取直接子节点
        sub = []
        for y in adj[rt]:
            if parent[y] == rt:  # 关键修正：确保只处理子节点
                sub.append((siz[y], y))
        sub.sort(reverse=True, key=lambda x: x[0])

        ans = [0]*(n+1)
        ans[rt] = 1

        # 递归求解答案
        def solve(x, F, sum_val, pre):
            if sum_val <= n//2:
                ans[x] = 1
            for i in range(min(2, len(sub))):
                s, node = sub[i]
                if node == pre:
                    continue
                if (n - siz[x] - s) <= n//2:
                    ans[x] = 1
            for y in adj[x]:
                if y == F:
                    continue
                solve(y, x, sum_val, pre)

        # 遍历所有子节点
        for y in adj[rt]:
            if parent[y] != rt:  # 关键修正：过滤非子节点
                continue
            solve(y, rt, n - siz[y], y)

        return ans[1:n+1]
