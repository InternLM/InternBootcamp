import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccutemall.Ccutemall_reward_calculator import CcutemallRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcutemallVerificationTool(BaseTool):
    """Ccutemall验证工具"""
    
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
            score = CcutemallRewardCalculator.verify_score(
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
            logger.error(f"CcutemallVerificationTool执行错误: {str(e)}")
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
    def generate_tree(self, n):
        """使用改进的Prüfer序列生成更平衡的树结构"""
        if n == 1:
            return []
        if n == 2:
            return [(1, 2)]

        # 生成更平衡的Prüfer序列
        prufer = []
        for _ in range(n-2):
            # 偏好选择中间节点
            prufer.append(random.randint(max(1, n//4), min(n, 3*n//4)))

        degree = [1]*(n+1)
        for node in prufer:
            degree[node] += 1

        edges = []
        for node in prufer:
            for v in range(1, n+1):
                if degree[v] == 1:
                    edges.append((node, v))
                    degree[node] -= 1
                    degree[v] -= 1
                    break

        # 处理剩余节点时保持随机性
        remaining = [v for v in range(1, n+1) if degree[v] == 1]
        edges.append((remaining.pop(), remaining.pop()))

        # 随机打乱边并确保节点顺序
        random.shuffle(edges)
        return [(u, v) if u < v else (v, u) for u, v in edges]

    def _calculate_solution(self, n, edges):
        """修正的DFS解法"""
        if n % 2 != 0:
            return -1

        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        self.count = 0

        def dfs(node, parent):
            size = 1
            for neighbor in adj[node]:
                if neighbor == parent:
                    continue
                child_size = dfs(neighbor, node)
                size += child_size
                if child_size % 2 == 0:
                    self.count += 1
            return size

        total_size = dfs(1, -1)
        # 验证总大小
        return self.count if total_size % 2 == 0 else -1
