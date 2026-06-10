import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.fnastyaandtimemachine.Fnastyaandtimemachine_reward_calculator import FnastyaandtimemachineRewardCalculator

# 导入依赖库
import random
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class FnastyaandtimemachineVerificationTool(BaseTool):
    """Fnastyaandtimemachine验证工具"""
    
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
            score = FnastyaandtimemachineRewardCalculator.verify_score(
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
            logger.error(f"FnastyaandtimemachineVerificationTool执行错误: {str(e)}")
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
    def _generate_tree(n):
        if n == 1:
            return []

        # 优化后的树生成算法
        nodes = list(range(1, n+1))
        if n == 2:
            return [(nodes[0], nodes[1])]

        # 改进的Prufer序列生成
        prufer = [random.choice(nodes) for _ in range(n-2)]
        degree = defaultdict(int)
        for node in prufer:
            degree[node] += 1

        adj = defaultdict(list)
        # 阶段1：处理Prufer序列
        for p in prufer:
            for v in nodes:
                if degree[v] == 0 and (p != v or degree[p] > 0):
                    adj[p].append(v)
                    adj[v].append(p)
                    degree[p] -= 1
                    degree[v] -= 1
                    break

        # 阶段2：处理剩余节点
        leaves = [v for v in nodes if degree[v] == 0]
        while len(leaves) >= 2:
            u = leaves.pop()
            v = leaves.pop()
            adj[u].append(v)
            adj[v].append(u)

        # 去重并排序边
        seen = set()
        edges = []
        for u in adj:
            for v in adj[u]:
                if u < v and (u, v) not in seen:
                    edges.append((u, v))
                    seen.add((u, v))
        return sorted(edges, key=lambda x: (x[0], x[1]))
