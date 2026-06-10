import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.eworldeaterbrothers.Eworldeaterbrothers_reward_calculator import EworldeaterbrothersRewardCalculator

# 导入依赖库
import re
from random import randint
from random import choice
from collections import defaultdict



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EworldeaterbrothersVerificationTool(BaseTool):
    """Eworldeaterbrothers验证工具"""
    
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
            score = EworldeaterbrothersRewardCalculator.verify_score(
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
            logger.error(f"EworldeaterbrothersVerificationTool执行错误: {str(e)}")
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
    def _calculate_min_reversals(n, edges):
        if n <= 1:
            return 0

        # 构建双向邻接表
        h = defaultdict(list)
        edge_dict = {}
        for idx, (a, b) in enumerate(edges):
            num = idx + 1
            h[a].append({'y':b, 'v':0, 'num':num})
            h[b].append({'y':a, 'v':1, 'num':num})
            edge_dict[num] = (a, b)

        # 第一遍DFS计算层级和初始cost
        floors = [0]*(n+1)
        f = [0]*(n+1)
        stack = [(1, 0, False)]
        while stack:
            node, parent, visited = stack.pop()
            if not visited:
                floors[node] = floors[parent] + 1
                stack.append((node, parent, True))
                # 按随机顺序处理子节点（避免生成链式结构）
                children = [edge for edge in h[node] if edge['y'] != parent]
                for edge in reversed(children):
                    stack.append((edge['y'], node, False))
            else:
                f[node] = 0
                for edge in h[node]:
                    if edge['y'] != parent:
                        f[node] += f[edge['y']] + edge['v']

        min_flips = float('inf')
        processed = set()

        # 遍历所有可能的切割边
        for num in edge_dict:
            if num in processed:
                continue
            processed.add(num)

            a, b = edge_dict[num]
            # 确定父子关系
            if floors[a] > floors[b]:
                parent, child = b, a
                original_dir = 1  # 当前方向是child->parent
            else:
                parent, child = a, b
                original_dir = 0  # 当前方向是parent->child

            # 计算上半部分的最小翻转
            upper_min = f[1] - f[child] - original_dir
            stack = [(1, 0, upper_min)]
            current_min = upper_min
            while stack:
                node, father, cost = stack.pop()
                current_min = min(current_min, cost)
                for edge in h[node]:
                    if edge['y'] != father and edge['num'] != num:
                        new_cost = cost - 1 if edge['v'] else cost + 1
                        stack.append((edge['y'], node, new_cost))

            # 计算下半部分的最小翻转
            lower_min = f[child]
            stack = [(child, parent, lower_min)]
            current_lower = lower_min
            while stack:
                node, father, cost = stack.pop()
                current_lower = min(current_lower, cost)
                for edge in h[node]:
                    if edge['y'] != father and edge['num'] != num:
                        new_cost = cost - 1 if edge['v'] else cost + 1
                        stack.append((edge['y'], node, new_cost))

            min_flips = min(min_flips, current_min + current_lower)

        return min_flips if min_flips != float('inf') else 0
