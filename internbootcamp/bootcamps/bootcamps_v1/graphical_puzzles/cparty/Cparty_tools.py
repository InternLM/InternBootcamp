import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cparty.Cparty_reward_calculator import CpartyRewardCalculator

# 导入依赖库
import re
import random
from itertools import combinations



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CpartyVerificationTool(BaseTool):
    """Cparty验证工具"""
    
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
            score = CpartyRewardCalculator.verify_score(
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
            logger.error(f"CpartyVerificationTool执行错误: {str(e)}")
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
    def _generate_connected_graph(self, n):
        """改进的连通图生成算法"""
        if n == 1:
            return []

        edges = set()
        nodes = list(range(1, n+1))
        visited = {nodes[0]}
        unvisited = set(nodes[1:])

        # Prim算法生成生成树
        while unvisited:
            u = random.choice(list(visited))
            v = random.choice(list(unvisited))
            edges.add(frozenset((u, v)))
            visited.add(v)
            unvisited.remove(v)

        # 添加随机边 (至少添加n-1条边)
        all_possible = {frozenset(e) for e in combinations(nodes, 2)}
        remaining = list(all_possible - edges)
        random.shuffle(remaining)

        extra = random.randint(0, len(remaining))
        edges.update(remaining[:extra])

        return sorted([sorted(list(e)) for e in edges])

    def _calculate_optimal_solution(self, n, edges):
        """基于位运算的高效算法（参考原题解）"""
        if n == 1:
            return 0, []

        # 转换为0-based邻接表
        adj = [0] * n
        for u, v in edges:
            u_idx = u - 1
            v_idx = v - 1
            adj[u_idx] |= 1 << v_idx
            adj[v_idx] |= 1 << u_idx

        # 添加自环
        for i in range(n):
            adj[i] |= 1 << i

        # 预处理覆盖关系
        full_mask = (1 << n) - 1
        if all(mask == full_mask for mask in adj):
            return 0, []

        # 初始化neigh数组
        max_mask = 1 << n
        coverage = [0] * max_mask
        for i in range(n):
            coverage[1 << i] = adj[i]

        # 预处理所有mask的覆盖关系
        for mask in range(max_mask):
            for i in range(n):
                if (mask & (1 << i)) and (coverage[mask ^ (1 << i)] & (1 << i)):
                    coverage[mask] = coverage[mask ^ (1 << i)] | adj[i]

        # 寻找最小集合
        best_mask = full_mask
        min_steps = n
        for mask in range(max_mask):
            if coverage[mask] == full_mask:
                cnt = bin(mask).count('1')
                if cnt < min_steps:
                    min_steps = cnt
                    best_mask = mask

        solution = [i+1 for i in range(n) if (best_mask & (1 << i))]
        return min_steps, solution
