import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eparty.Eparty_reward_calculator import EpartyRewardCalculator

# 导入依赖库
import random
from collections import deque
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EpartyVerificationTool(BaseTool):
    """Eparty验证工具"""
    
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
            score = EpartyRewardCalculator.verify_score(
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
            logger.error(f"EpartyVerificationTool执行错误: {str(e)}")
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
    def _generate_connected_graph(n):
        edges = set()
        nodes = list(range(1, n+1))
        random.shuffle(nodes)

        # Generate a spanning tree
        for i in range(1, n):
            j = random.randint(0, i-1)
            u, v = sorted((nodes[j], nodes[i]))
            edges.add((u, v))

        # Add additional edges
        all_edges = [(u, v) for u in range(1, n+1) for v in range(u+1, n+1)]
        remaining = [e for e in all_edges if e not in edges]
        max_possible = n * (n-1) // 2
        m = random.randint(n-1, max_possible)
        edges.update(random.sample(remaining, k=m - (n-1)))

        return sorted(edges)

    @staticmethod
    def _solve_min_steps(n, edges):
        edges_list = [(u, v) for u in range(1, n+1) for v in range(u+1, n+1)]
        edge_to_bit = {e: i for i, e in enumerate(edges_list)}

        initial_mask = 0
        for u, v in edges:
            initial_mask |= 1 << edge_to_bit[(u, v) if u < v else (v, u)]

        target = (1 << len(edges_list)) - 1
        if initial_mask == target:
            return 0

        visited = {initial_mask: 0}
        queue = deque([(initial_mask, 0)])

        while queue:
            mask, steps = queue.popleft()

            for a in range(1, n+1):
                friends = set()
                for u in range(1, n+1):
                    if u == a:
                        continue
                    e = tuple(sorted((a, u)))
                    if mask & (1 << edge_to_bit[e]):
                        friends.add(u)

                friends.add(a)
                new_mask = mask
                for i in friends:
                    for j in friends:
                        if i < j:
                            new_mask |= 1 << edge_to_bit[(i, j)]

                if new_mask == target:
                    return steps + 1
                if new_mask not in visited or steps + 1 < visited[new_mask]:
                    visited[new_mask] = steps + 1
                    queue.append((new_mask, steps + 1))

        return n  # Fallback
