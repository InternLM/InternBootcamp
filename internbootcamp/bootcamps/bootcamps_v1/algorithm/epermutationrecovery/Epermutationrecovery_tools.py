import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.epermutationrecovery.Epermutationrecovery_reward_calculator import EpermutationrecoveryRewardCalculator

# 导入依赖库
import random
import re
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EpermutationrecoveryVerificationTool(BaseTool):
    """Epermutationrecovery验证工具"""
    
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
            score = EpermutationrecoveryRewardCalculator.verify_score(
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
            logger.error(f"EpermutationrecoveryVerificationTool执行错误: {str(e)}")
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
    def _generate_solvable_case(self):
        n = random.randint(*self.n_range)
        p = list(range(1, n+1))
        random.shuffle(p)
        next_list = self.compute_next(p)
        masked_next = [
            x if random.random() < self.mask_prob else -1
            for x in next_list
        ]
        return {'n': n, 'next': masked_next}

    def _generate_unsolvable_case(self):
        conflict_types = [
            self._create_cycle_conflict,
            self._create_order_conflict,
            self._create_range_conflict
        ]
        for _ in range(50):
            creator = random.choice(conflict_types)
            case = creator()
            if case and not self.check_solvable(case['n'], case['next']):
                return case
        return {'n': 3, 'next': [3, 4, -1]}

    def _create_cycle_conflict(self):
        n = random.randint(3, 6)
        next_list = [-1]*n
        for i in range(n-1):
            next_list[i] = i+2  # 创建循环依赖
        next_list[-1] = 1
        return {'n': n, 'next': next_list}

    def _create_order_conflict(self):
        n = random.randint(4, 6)
        next_list = [-1]*n
        next_list[0] = n+1  # 无效的next值
        for i in range(1, n-1):
            next_list[i] = i+2
        return {'n': n, 'next': next_list}

    def _create_range_conflict(self):
        n = 5
        return {'n': n, 'next': [3, 6, 4, 6, -1]}

    @staticmethod
    def compute_next(p):
        n = len(p)
        next_arr = []
        for i in range(n):
            min_j = n + 1
            for j in range(i+1, n):
                if p[j] > p[i]:
                    min_j = j + 1
                    break
            next_arr.append(min_j)
        return next_arr

    @staticmethod
    def check_solvable(n, next_list):
        next_array = [x-1 if x != -1 else -1 for x in next_list]
        graph = [[] for _ in range(n)]
        stack = []

        # 构建图结构
        for i in range(n):
            if 0 <= next_array[i] < n:
                graph[i].append(next_array[i])

            while stack and (next_array[stack[-1]] == -1 or next_array[stack[-1]] <= i):
                stack.pop()
            if stack:
                graph[i].append(stack[-1])
            if next_array[i] != -1 and next_array[i] != n:
                stack.append(i)

        # 拓扑排序检测
        in_degree = [0]*n
        for u in range(n):
            for v in graph[u]:
                if 0 <= v < n:
                    in_degree[v] += 1

        queue = deque([u for u in range(n) if in_degree[u] == 0])
        visited = 0

        while queue:
            u = queue.popleft()
            visited += 1
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    queue.append(v)

        return visited == n
