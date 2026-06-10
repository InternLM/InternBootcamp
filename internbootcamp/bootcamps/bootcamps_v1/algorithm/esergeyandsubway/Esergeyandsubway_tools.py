import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.esergeyandsubway.Esergeyandsubway_reward_calculator import EsergeyandsubwayRewardCalculator

# 导入依赖库
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EsergeyandsubwayVerificationTool(BaseTool):
    """Esergeyandsubway验证工具"""
    
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
            score = EsergeyandsubwayRewardCalculator.verify_score(
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
            logger.error(f"EsergeyandsubwayVerificationTool执行错误: {str(e)}")
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
        """
        使用Prüfer序列生成随机树。
        """
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]

        prufer = [random.randint(1, n) for _ in range(n-2)]
        degree = [0] * (n + 1)
        for node in prufer:
            degree[node] += 1

        leaves = []
        for i in range(1, n + 1):
            if degree[i] == 0:
                leaves.append(i)

        edges = []
        for node in prufer:
            leaf = leaves.pop(0)
            edges.append((leaf, node))
            degree[node] -= 1
            if degree[node] == 0:
                leaves.append(node)
            leaves.sort()

        edges.append((leaves[0], leaves[1]))
        return edges

    @staticmethod
    def solve(n, edges_list):
        """
        根据给定的树结构计算正确的结果。
        """
        adj = [[] for _ in range(n+1)]
        for a, b in edges_list:
            adj[a].append(b)
            adj[b].append(a)

        root = 1
        q = [root]
        odd = [0] * (n+1)
        even = [0] * (n+1)
        odd_size = [0] * (n+1)
        even_size = [1] * (n+1)
        rank = [0] * (n+1)
        rank[root] = 1

        i = 0
        while i < len(q):
            node = q[i]
            for v in adj[node]:
                if rank[v] == 0:
                    rank[v] = rank[node] + 1
                    q.append(v)
            i += 1

        for node in reversed(q):
            for v in adj[node]:
                if rank[v] > rank[node]:
                    odd[node] += even[v] + even_size[v]
                    even[node] += odd[v] + odd_size[v]
                    even_size[node] += odd_size[v]
                    odd_size[node] += even_size[v]

        for node in q:
            for v in adj[node]:
                if rank[v] > rank[node]:
                    deven = odd[node] - (even[v] + even_size[v]) + (odd_size[node] - even_size[v])
                    dodd = even[node] - (odd[v] + odd_size[v]) + (even_size[node] - odd_size[v])
                    even[v] += deven
                    odd[v] += dodd
                    even_size[v] = odd_size[node]
                    odd_size[v] = even_size[node]

        ans = 0
        for i in range(1, n+1):
            ans += even[i] // 2
            ans += (odd[i] + odd_size[i]) // 2
        ans = ans // 2
        return ans
