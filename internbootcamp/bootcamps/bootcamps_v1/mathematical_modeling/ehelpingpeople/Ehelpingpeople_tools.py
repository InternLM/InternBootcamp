import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.ehelpingpeople.Ehelpingpeople_reward_calculator import EhelpingpeopleRewardCalculator

# 导入依赖库
import random
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EhelpingpeopleVerificationTool(BaseTool):
    """Ehelpingpeople验证工具"""
    
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
            score = EhelpingpeopleRewardCalculator.verify_score(
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
            logger.error(f"EhelpingpeopleVerificationTool执行错误: {str(e)}")
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
    def _calculate(self, n, a, recommendations):
        class Segment:
            def __init__(self, a, b, p):
                self.a = a-1  # 0-based
                self.b = b-1
                self.p = p
                self.children = []
                self.maxv = 0
                self.dist = {}

            def solve(self, values):
                # Calculate base maximum
                self.maxv = max(values[self.a:self.b+1])

                # Process children
                prev_end = self.a-1
                for child in self.children:
                    # Left gap
                    if prev_end+1 <= child.a-1:
                        self.maxv = max(self.maxv, max(values[prev_end+1:child.a]))
                    # Child's maximum (after solving)
                    child.solve(values)
                    self.maxv = max(self.maxv, child.maxv)
                    prev_end = child.b
                # Right gap
                if prev_end+1 <= self.b:
                    self.maxv = max(self.maxv, max(values[prev_end+1:self.b+1]))

                # Initialize distribution
                self.dist = {self.maxv: 1.0}

                # Merge children distributions
                for child in self.children:
                    new_dist = {}
                    for k1, p1 in self.dist.items():
                        for k2, p2 in child.dist.items():
                            key = max(k1, k2)
                            prob = p1 * p2
                            new_dist[key] = new_dist.get(key, 0.0) + prob
                    self.dist = new_dist

                # Apply current probability
                if self.p > 0:
                    new_dist = {}
                    for k, p in self.dist.items():
                        new_dist[k+1] = new_dist.get(k+1, 0.0) + p * self.p
                        new_dist[k] = new_dist.get(k, 0.0) + p * (1 - self.p)
                    self.dist = new_dist
                    self.maxv += 1

        # Build interval tree
        segs = [Segment(1, n, 0.0)] + [Segment(l, r, p) for l, r, p in recommendations]
        segs.sort(key=lambda x: (x.a, -(x.b - x.a)))

        # Build hierarchy
        stack = [segs[0]]
        for s in segs[1:]:
            while stack and not (stack[-1].a <= s.a and s.b <= stack[-1].b):
                stack.pop()
            if stack:
                stack[-1].children.append(s)
            stack.append(s)

        # Solve root
        segs[0].solve(a)
        expectation = sum(k * p for k, p in segs[0].dist.items())
        return expectation
