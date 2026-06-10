import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.cknights.Cknights_reward_calculator import CknightsRewardCalculator

# 导入依赖库
import re
import random
from collections import defaultdict
from collections import deque

# === 源文件中的全局函数 ===

def simulate_knights_placement(initial_knights):
    current_knights = set()
    coords = [tuple(knight) for knight in initial_knights]
    if len(coords) != len(set(coords)):
        return 0
    for x, y in coords:
        if not (-1e9 <= x <= 1e9 and -1e9 <= y <= 1e9):
            return 0
    current_knights = set(coords)
    knight_moves = [(1,2), (1,-2), (-1,2), (-1,-2), (2,1), (2,-1), (-2,1), (-2,-1)]
    attack_counts = defaultdict(int)
    for x, y in current_knights:
        for dx, dy in knight_moves:
            neighbor = (x + dx, y + dy)
            attack_counts[neighbor] += 1
    queue = deque()
    in_queue = set()
    for cell in attack_counts:
        if attack_counts[cell] >=4 and cell not in current_knights:
            queue.append(cell)
            in_queue.add(cell)
    while queue:
        cell = queue.popleft()
        in_queue.discard(cell)
        if cell in current_knights:
            continue
        if attack_counts[cell] <4:
            continue
        current_knights.add(cell)
        for dx, dy in knight_moves:
            neighbor = (cell[0] + dx, cell[1] + dy)
            attack_counts[neighbor] += 1
            if attack_counts[neighbor] >=4 and neighbor not in current_knights and neighbor not in in_queue:
                queue.append(neighbor)
                in_queue.add(neighbor)
    return len(current_knights)

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CknightsVerificationTool(BaseTool):
    """Cknights验证工具"""
    
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
            score = CknightsRewardCalculator.verify_score(
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
            logger.error(f"CknightsVerificationTool执行错误: {str(e)}")
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

