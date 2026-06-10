import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.cmatrixsorting.Cmatrixsorting_reward_calculator import CmatrixsortingRewardCalculator

# 导入依赖库
import random
import re
from copy import deepcopy
from typing import List
from typing import Union



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CmatrixsortingVerificationTool(BaseTool):
    """Cmatrixsorting验证工具"""
    
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
            score = CmatrixsortingRewardCalculator.verify_score(
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
            logger.error(f"CmatrixsortingVerificationTool执行错误: {str(e)}")
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
    def _generate_matrix(self):
        return [[random.randint(1, self.n) for _ in range(self.m)] 
                for _ in range(self.n)]

    def _generate_sorting_columns(self):
        return random.choices(range(1, self.m+1), 
                            k=random.randint(0, self.m))

    def _apply_sorting(self, matrix, columns):
        sorted_mat = deepcopy(matrix)
        for col in columns:
            sorted_mat.sort(key=lambda row: row[col-1])
        return sorted_mat

    def _corrupt_matrix(self, A, B):  # 统一方法名称
        B_prime = deepcopy(B)
        A_rows = {tuple(row) for row in A}

        # 确保至少存在一个非法行
        for i in range(self.n):
            if tuple(B_prime[i]) not in A_rows:
                continue

            for j in range(self.m):
                for v in range(1, self.n+2):
                    new_row = list(B_prime[i])
                    new_row[j] = v
                    if tuple(new_row) not in A_rows:
                        B_prime[i] = new_row
                        return B_prime

        # 最终保护：随机生成全新行
        while True:
            new_row = [random.randint(1, self.n+1) for _ in range(self.m)]
            if tuple(new_row) not in A_rows:
                B_prime[random.randint(0, self.n-1)] = new_row
                return B_prime
