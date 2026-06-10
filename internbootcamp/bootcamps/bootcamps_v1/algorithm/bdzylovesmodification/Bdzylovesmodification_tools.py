import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.bdzylovesmodification.Bdzylovesmodification_reward_calculator import BdzylovesmodificationRewardCalculator

# 导入依赖库
import heapq
from heapq import heappush
from heapq import heappop
import random

# === 源文件中的全局函数 ===

def calculate_max_pleasure(n, m, k, p, matrix):
    # 计算初始行和列的总和
    row_sums = [sum(row) for row in matrix]
    col_sums = [sum(matrix[i][j] for i in range(n)) for j in range(m)]

    # 初始化最大堆（使用负数实现最小堆模拟最大堆）
    row_heap = [-s for s in row_sums]
    heapq.heapify(row_heap)
    col_heap = [-s for s in col_sums]
    heapq.heapify(col_heap)

    # 预计算所有可能的行操作收益
    pr = {0: 0}
    current_sum = 0
    for h in range(1, k+1):
        if not row_heap:
            break
        current = -heappop(row_heap)
        current_sum += current
        pr[h] = current_sum
        heappush(row_heap, -(current - m*p))  # 更新行总和

    # 预计算所有可能的列操作收益
    pc = {0: 0}
    current_sum = 0
    for h in range(1, k+1):
        if not col_heap:
            break
        current = -heappop(col_heap)
        current_sum += current
        pc[h] = current_sum
        heappush(col_heap, -(current - n*p))  # 更新列总和

    # 穷举所有可能的行、列操作组合
    max_total = -float('inf')
    for i in pr:
        j = k - i
        if j >= 0 and j in pc:
            total = pr[i] + pc[j] - i*j*p
            max_total = max(max_total, total)
    
    return max_total if max_total != -float('inf') else 0

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class BdzylovesmodificationVerificationTool(BaseTool):
    """Bdzylovesmodification验证工具"""
    
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
            score = BdzylovesmodificationRewardCalculator.verify_score(
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
            logger.error(f"BdzylovesmodificationVerificationTool执行错误: {str(e)}")
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

