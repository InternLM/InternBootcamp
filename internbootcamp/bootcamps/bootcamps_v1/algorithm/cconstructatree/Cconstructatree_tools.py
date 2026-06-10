import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cconstructatree.Cconstructatree_reward_calculator import CconstructatreeRewardCalculator

# 导入依赖库
import random
from collections import defaultdict
import re



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CconstructatreeVerificationTool(BaseTool):
    """Cconstructatree验证工具"""
    
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
            score = CconstructatreeRewardCalculator.verify_score(
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
            logger.error(f"CconstructatreeVerificationTool执行错误: {str(e)}")
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
    def generate_solution(n, s):
        if s < 2 * n -1 or s > n * (n + 1) // 2:
            return {'possible': False}

        left = 0
        right = n - 1
        d_final = None
        answer_r = None

        while right - left > 1:
            mid = (left + right) // 2
            possible, d = Cconstructatreebootcamp.go(mid, n, s)
            if possible:
                right = mid
            else:
                left = mid

        possible, d = Cconstructatreebootcamp.go(right, n, s)
        if not possible:
            possible_left, d_left = Cconstructatreebootcamp.go(left, n, s)
            if possible_left:
                right = left
                d = d_left
            else:
                return {'possible': False}

        p_array = Cconstructatreebootcamp.construct_p(n, right, d)
        children = defaultdict(list)
        for i in range(2, n + 1):
            parent = p_array[i-2]
            children[parent].append(i)
        max_degree = max(len(v) for v in children.values()) if children else 0

        return {
            'possible': True,
            'p_array': p_array,
            'k': right,
            'max_degree': max_degree
        }

    @staticmethod
    def go(deg, n, s):
        he = 2
        curs = s
        curs -= 1  # Root node's contribution
        already = 0
        can = deg
        d = [0] * (n + 1)
        d[1] = 1  # Depth of root is 1

        for i in range(2, n + 1):
            if already == can:
                he += 1
                already = 0
                can *= deg

            remaining_nodes = n - i
            mx_term = (2 * he + remaining_nodes) * (remaining_nodes) // 2

            if curs <= he + mx_term:
                already += 1
                d[i] = he
                curs -= he
            else:
                he += 1
                d[i] = he
                curs -= he

        return curs == 0, d

    @staticmethod
    def construct_p(n, r, d):
        can = [r] * (n + 2)
        le = 1
        p = [0] * (n + 1)

        for i in range(2, n + 1):
            while le <= n and can[le] == 0:
                le += 1

            while le < i and d[le] + 1 < d[i]:
                le += 1

            p[i] = le
            can[le] -= 1

        return p[2:n+1]
