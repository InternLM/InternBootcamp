import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.clatinsquare.Clatinsquare_reward_calculator import ClatinsquareRewardCalculator

# 导入依赖库
import re
import json
from random import randint
from random import choices
from random import shuffle
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class ClatinsquareVerificationTool(BaseTool):
    """Clatinsquare验证工具"""
    
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
            score = ClatinsquareRewardCalculator.verify_score(
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
            logger.error(f"ClatinsquareVerificationTool执行错误: {str(e)}")
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
    def _compute_final(cls, n, initial_matrix, operations):
        # 转换为0-based索引
        v = [[x-1 for x in row] for row in initial_matrix]
        e = [0, 0, 0]  # 行、列、值的偏移量
        p = [0, 1, 2]  # 映射顺序：行、列、值

        for c in operations:
            if c == 'R':
                e[p[1]] = (e[p[1]] + 1) % n
            elif c == 'L':
                e[p[1]] = (e[p[1]] - 1) % n
            elif c == 'D':
                e[p[0]] = (e[p[0]] + 1) % n
            elif c == 'U':
                e[p[0]] = (e[p[0]] - 1) % n
            elif c == 'I':
                p[1], p[2] = p[2], p[1]  # 交换列和值的映射
            elif c == 'C':
                p[0], p[2] = p[2], p[0]  # 交换行和值的映射

        # 生成最终矩阵
        w = [[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                # 原始坐标和值
                z = [i, j, v[i][j]]
                # 应用偏移和映射后的坐标
                I = (z[p[0]] + e[p[0]]) % n
                J = (z[p[1]] + e[p[1]]) % n
                K = (z[p[2]] + e[p[2]]) % n
                w[I][J] = K + 1  # 转换回1-based
        return w
