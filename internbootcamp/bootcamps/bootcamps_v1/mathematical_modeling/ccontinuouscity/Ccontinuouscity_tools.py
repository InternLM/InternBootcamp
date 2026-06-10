import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.ccontinuouscity.Ccontinuouscity_reward_calculator import CcontinuouscityRewardCalculator

# 导入依赖库
import random
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Set



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CcontinuouscityVerificationTool(BaseTool):
    """Ccontinuouscity验证工具"""
    
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
            score = CcontinuouscityRewardCalculator.verify_score(
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
            logger.error(f"CcontinuouscityVerificationTool执行错误: {str(e)}")
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
    def construct_valid_structure(self, L: int, R: int) -> Tuple[bool, Optional[Dict]]:
        """实现完整的结构构造逻辑"""
        n = 32
        edges = []
        cl = [0] * (n-1)
        cr = [1] * (n-1)

        # 初始化第一个块
        edges.append((1, n, L))
        current_L = L + 1

        for vi in range(1, 30):  # 构造中间块
            if current_L > R:
                break

            max_step = min(1 << (vi-1), R - current_L + 1)
            if max_step <= 0:
                break

            cl[vi] = cr[vi-1]
            cr[vi] = cl[vi]

            # 连接所有之前的块
            for j in range(vi-1, -1, -1):
                delta = cr[j] - cl[j]
                if cr[vi] + delta <= cl[vi] + max_step:
                    edges.append((j+1, vi+1, cr[vi] - cl[j]))
                    cr[vi] += delta

            # 添加到终点的边
            edge_weight = current_L - cl[vi]
            edges.append((vi+1, n, edge_weight))
            current_L += max_step

        if current_L - 1 < R:
            return False, None

        return True, {
            'n': n,
            'm': len(edges),
            'edges': edges
        }

    @staticmethod
    def validate_paths(n: int, edges: List[Tuple[int,int,int]], L: int, R: int) -> bool:
        """优化的路径验证算法"""
        # 构建邻接表
        adj = [[] for _ in range(n+1)]
        edge_map = {}
        for a, b, c in edges:
            adj[a].append((b, c))
            edge_map[(a,b)] = c

        # 使用动态规划计算所有路径长度
        dp = [set() for _ in range(n+1)]
        dp[1].add(0)

        for u in range(1, n+1):
            if not dp[u]:
                continue
            for v, w in adj[u]:
                dp[v].update({path_len + w for path_len in dp[u]})

        all_lengths = dp[n]
        if not all_lengths:
            return False

        # 检查范围
        min_len = min(all_lengths)
        max_len = max(all_lengths)
        if min_len != L or max_len != R:
            return False

        # 检查连续性和唯一性
        expected = set(range(L, R+1))
        return all_lengths == expected
