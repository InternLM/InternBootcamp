import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.dstrangehousing.Dstrangehousing_reward_calculator import DstrangehousingRewardCalculator

# 导入依赖库
import random
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DstrangehousingVerificationTool(BaseTool):
    """Dstrangehousing验证工具"""
    
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
            score = DstrangehousingRewardCalculator.verify_score(
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
            logger.error(f"DstrangehousingVerificationTool执行错误: {str(e)}")
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
    def _generate_valid_case(self):
        """生成保证有解的连通二分图"""
        n = random.randint(3, self.max_houses)
        partition = {i: i%2 for i in range(1, n+1)}  # 简单二分

        # 确保图连通
        edges = []
        visited = set([1])
        queue = deque([1])

        while len(visited) < n:
            u = queue.popleft()
            candidates = [v for v in range(1, n+1) 
                        if v not in visited and partition[v] != partition[u]]
            if candidates:
                v = random.choice(candidates)
                edges.append((u, v))
                visited.add(v)
                queue.append(v)
            else:  # 添加跨分区边保持连通
                for v in range(1, n+1):
                    if v not in visited and partition[v] == partition[u]:
                        edges.append((u, v))
                        visited.add(v)
                        queue.append(v)
                        break

        # 添加额外边（保持二分性）
        possible_edges = []
        for u in range(1, n):
            for v in range(u+1, n+1):
                if partition[u] != partition[v] and (u, v) not in edges:
                    possible_edges.append((u, v))

        add_num = min(len(possible_edges), self.max_paths - len(edges))
        edges.extend(random.sample(possible_edges, add_num))

        return {'n': n, 'm': len(edges), 'edges': edges}

    def _generate_invalid_case(self):
        """生成包含奇数环的不可解案例"""
        cycle_size = random.choice([3, 5, 7])
        n = cycle_size
        edges = [(i, i%cycle_size +1) for i in range(1, cycle_size+1)]

        # 添加额外边保持连通
        for _ in range(random.randint(0, 3)):
            u = random.randint(1, n)
            v = random.randint(1, n)
            if u != v and (u, v) not in edges and (v, u) not in edges:
                edges.append((u, v))

        return {'n': n, 'm': len(edges), 'edges': edges}

    @classmethod
    def _is_bipartite(cls, edges, n):
        """判断是否为二分图（可解条件）"""
        color = {}
        adj = {u: [] for u in range(1, n+1)}
        for u, v in edges:
            adj[u].append(v)
            adj[v].append(u)

        for u in range(1, n+1):
            if u not in color:
                queue = deque([u])
                color[u] = 0
                while queue:
                    current = queue.popleft()
                    for neighbor in adj[current]:
                        if neighbor not in color:
                            color[neighbor] = color[current] ^ 1
                            queue.append(neighbor)
                        elif color[neighbor] == color[current]:
                            return False
        return True
