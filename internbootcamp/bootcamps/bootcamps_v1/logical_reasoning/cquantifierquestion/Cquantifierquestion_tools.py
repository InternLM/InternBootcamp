import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.logical_reasoning.cquantifierquestion.Cquantifierquestion_reward_calculator import CquantifierquestionRewardCalculator

# 导入依赖库
import random
import re
from collections import deque



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CquantifierquestionVerificationTool(BaseTool):
    """Cquantifierquestion验证工具"""
    
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
            score = CquantifierquestionRewardCalculator.verify_score(
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
            logger.error(f"CquantifierquestionVerificationTool执行错误: {str(e)}")
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
    @classmethod
    def reference_solution(cls, identity):
        # 完全复制参考代码逻辑
        def toposort(graph):
            n = len(graph)
            res = []
            found = [0]*n

            for i in range(n):
                if found[i]:
                    continue
                stack = [i]
                while stack:
                    node = stack.pop()
                    if node < 0:
                        res.append(~node)
                    elif not found[node]:
                        found[node] = 1
                        stack.append(~node)
                        for nei in graph[node]:
                            if not found[nei]:
                                stack.append(nei)

            # Check cycle
            found = [0]*n
            for node in res:
                if found[node]:
                    return None
                stack = [node]
                found[node] = 1
                while stack:
                    current = stack.pop()
                    for nei in graph[current]:
                        if found[nei]:
                            return None
                        if not found[nei]:
                            found[nei] = 1
                            stack.append(nei)
            return res[::-1]

        n = identity['n']
        edges = identity['edges']
        coupl1 = [[] for _ in range(n)]
        coupl2 = [[] for _ in range(n)]
        for j, k in edges:
            u = j - 1
            v = k - 1
            coupl1[u].append(v)
            coupl2[v].append(u)

        order = toposort(coupl1)
        if order is None:
            return -1

        seen1 = list(range(n))
        seen2 = list(range(n))

        for node in order:
            for nei in coupl1[node]:
                if seen1[nei] > seen1[node]:
                    seen1[nei] = seen1[node]

        for node in reversed(order):
            for nei in coupl2[node]:
                if seen2[nei] > seen2[node]:
                    seen2[nei] = seen2[node]

        seen = [(seen1[i] == i and seen2[i] == i) for i in range(n)]
        count = sum(seen)
        if count == 0:
            return -1
        quant = ''.join('A' if c else 'E' for c in seen)
        return (count, quant)
