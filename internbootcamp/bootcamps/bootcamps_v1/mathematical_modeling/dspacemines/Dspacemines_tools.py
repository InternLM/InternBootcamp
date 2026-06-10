import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.dspacemines.Dspacemines_reward_calculator import DspaceminesRewardCalculator

# 导入依赖库
import math
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class DspaceminesVerificationTool(BaseTool):
    """Dspacemines验证工具"""
    
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
            score = DspaceminesRewardCalculator.verify_score(
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
            logger.error(f"DspaceminesVerificationTool执行错误: {str(e)}")
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
    def generate_random_A(self):
        return (
            random.randint(-10000, 10000),
            random.randint(-10000, 10000),
            random.randint(-10000, 10000)
        )

    def generate_random_v(self):
        while True:
            v = (random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10))
            if any(v):
                return v

    def generate_mine(self, A, R, existing_mines):
        max_attempts = 1000
        for _ in range(max_attempts):
            # 生成随机方向和距离
            theta = random.uniform(0, math.pi)
            phi = random.uniform(0, 2*math.pi)
            dx = math.sin(theta)*math.cos(phi)
            dy = math.sin(theta)*math.sin(phi)
            dz = math.cos(theta)

            r_i = random.randint(1, R-1)
            min_dist = R + r_i + 1
            distance = random.uniform(min_dist, 2*min_dist)  # 生成适中距离

            ox = A[0] + dx*distance
            oy = A[1] + dy*distance
            oz = A[2] + dz*distance
            ox, oy, oz = int(round(ox)), int(round(oy)), int(round(oz))

            # 检查与已有地雷的间距
            valid = True
            for mine in existing_mines:
                mo = mine['O']
                mr = mine['r']
                dist_sq = (ox-mo[0])**2 + (oy-mo[1])**2 + (oz-mo[2])**2
                if dist_sq < (r_i + mr)**2:
                    valid = False
                    break
            if valid:
                return {
                    'O': [ox, oy, oz],
                    'r': r_i,
                    'm': random.randint(0, 10),
                    'spikes': [[random.randint(-10,10) for _ in range(3)] 
                              for _ in range(random.randint(0, 10))]
                }
        return None
