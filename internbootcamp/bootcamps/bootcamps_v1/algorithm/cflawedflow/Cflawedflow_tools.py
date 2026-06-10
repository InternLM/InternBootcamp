import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cflawedflow.Cflawedflow_reward_calculator import CflawedflowRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
from collections import deque

# === 源文件中的其他类 ===

class Edge:
    def __init__(self, from_, to_, w_, id_):
        self.from_ = from_
        self.to_ = to_
        self.w_ = w_
        self.id_ = id_

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CflawedflowVerificationTool(BaseTool):
    """Cflawedflow验证工具"""
    
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
            score = CflawedflowRewardCalculator.verify_score(
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
            logger.error(f"CflawedflowVerificationTool执行错误: {str(e)}")
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
    def _generate_connected_edges(n, m):
        parent = list(range(n+1))

        def find(u):
            if parent[u] != u:
                parent[u] = find(parent[u])
            return parent[u]

        edges = []
        existing = set()

        # Generate spanning tree to ensure connectivity
        nodes = list(range(1, n+1))
        random.shuffle(nodes)
        root = nodes[0]
        for node in nodes[1:]:
            a, b = root, node
            if a > b:
                a, b = b, a
            c = random.randint(1, 10000)
            edges.append((a, b, c))
            existing.add((a, b))
            parent[b] = a

        # Add remaining edges
        remaining = m - (n-1)
        candidates = [(i, j) for i in range(1, n+1) for j in range(i+1, n+1) if (i, j) not in existing]
        while remaining > 0 and candidates:
            add_num = min(remaining, len(candidates))
            selected = random.sample(candidates, add_num)
            for a, b in selected:
                c = random.randint(1, 10000)
                edges.append((a, b, c))
                existing.add((a, b))
                candidates.remove((a, b))  # Prevent duplicate selection
            remaining -= add_num

        random.shuffle(edges)
        return edges[:m]

    @staticmethod
    def _generate_solution(n, edges):
        m = len(edges)
        graph = [[] for _ in range(n+1)]
        wall = [0]*(n+1)
        for idx, (a, b, c) in enumerate(edges):
            edge = Edge(a, b, c, idx)
            graph[a].append(edge)
            graph[b].append(edge)
            wall[a] += c
            wall[b] += c

        ans = [-1]*m
        win = [0]*(n+1)
        q = deque([1])

        while q:
            u = q.popleft()
            to_check = []
            for edge in graph[u]:
                if ans[edge.id_] != -1:
                    continue
                if edge.from_ == u:
                    v = edge.to_
                    ans[edge.id_] = 0
                else:
                    v = edge.from_
                    ans[edge.id_] = 1
                win[v] += edge.w_
                wall[v] -= edge.w_
                if v != n:
                    to_check.append(v)

            for v in to_check:
                if win[v] == wall[v]:
                    q.append(v)

        return ans
