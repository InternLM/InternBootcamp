import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.epackagedelivery.Epackagedelivery_reward_calculator import EpackagedeliveryRewardCalculator

# 导入依赖库
import heapq
import random
import re

# === 源文件中的全局函数 ===

def compute_min_cost(d, n, stations):
    stations = sorted(stations, key=lambda x: x[0])
    # Add start and end points
    stations = [(0, 0)] + stations + [(d, 0)]
    heap = []
    total_cost = 0
    current_fuel = n  # 初始满油
    prev_pos = 0
    
    for i in range(1, len(stations)):
        current_pos, price = stations[i]
        distance = current_pos - prev_pos
        
        # Consume fuel for this distance
        current_fuel -= distance
        
        # Need to refuel if current_fuel < 0
        while current_fuel < 0:
            if not heap:
                return -1
            # Get cheapest fuel station
            p, pos = heapq.heappop(heap)
            # Calculate maximum fuel can be taken from this station
            max_refuel = min(-current_fuel, n - (prev_pos - pos))
            total_cost += max_refuel * p
            current_fuel += max_refuel
        
        if current_fuel < 0:
            return -1
        
        # Add current station to heap
        if i < len(stations)-1:  # 终点不加入堆
            heapq.heappush(heap, (price, current_pos))
        prev_pos = current_pos
    
    return total_cost

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EpackagedeliveryVerificationTool(BaseTool):
    """Epackagedelivery验证工具"""
    
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
            score = EpackagedeliveryRewardCalculator.verify_score(
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
            logger.error(f"EpackagedeliveryVerificationTool执行错误: {str(e)}")
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

