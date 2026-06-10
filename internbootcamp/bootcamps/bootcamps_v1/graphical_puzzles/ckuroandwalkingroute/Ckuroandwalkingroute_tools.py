import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.ckuroandwalkingroute.Ckuroandwalkingroute_reward_calculator import CkuroandwalkingrouteRewardCalculator

# 导入依赖库
import random
from collections import deque
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CkuroandwalkingrouteVerificationTool(BaseTool):
    """Ckuroandwalkingroute验证工具"""
    
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
            score = CkuroandwalkingrouteRewardCalculator.verify_score(
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
            logger.error(f"CkuroandwalkingrouteVerificationTool执行错误: {str(e)}")
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
    def _compute_under_except(self, adj, start, end):
        """
        计算underExcept值：从start出发不经过通向end路径的子树大小
        """
        if start == end:
            return 0

        path = self._find_path(adj, start, end)
        if not path:
            return 0

        next_node = path[1] if len(path) > 1 else None
        total = 1  # 包含start自己

        for neighbor in adj[start]:
            if neighbor == next_node:
                continue

            # 计算该邻接点子树的节点数
            count = 0
            visited = {start}
            stack = [neighbor]
            while stack:
                node = stack.pop()
                if node in visited:
                    continue
                visited.add(node)
                count += 1
                for v in adj[node]:
                    if v not in visited:
                        stack.append(v)
            total += count

        return total

    def _find_path(self, adj, start, end):
        """
        使用BFS找到start到end的路径
        """
        parent = {}
        queue = deque([start])
        parent[start] = None

        while queue:
            u = queue.popleft()
            if u == end:
                break
            for v in adj[u]:
                if v not in parent and v != parent.get(u):
                    parent[v] = u
                    queue.append(v)

        if end not in parent:
            return []

        # 重建路径
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = parent[current]
        return path[::-1]
