import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eoptimalpolygonperimeter.Eoptimalpolygonperimeter_reward_calculator import EoptimalpolygonperimeterRewardCalculator

# 导入依赖库
import re
import random
import math



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class EoptimalpolygonperimeterVerificationTool(BaseTool):
    """Eoptimalpolygonperimeter验证工具"""
    
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
            score = EoptimalpolygonperimeterRewardCalculator.verify_score(
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
            logger.error(f"EoptimalpolygonperimeterVerificationTool执行错误: {str(e)}")
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
    def generate_convex_polygon(self, n):
        """生成严格凸多边形，确保无三点共线"""
        while True:
            # 生成随机点并计算凸包
            points = []
            for _ in range(n*2):  # 生成足够多的点以提高找到严格凸包的概率
                x = random.randint(-100, 100)
                y = random.randint(-100, 100)
                if (x, y) not in points:
                    points.append((x, y))

            # 计算凸包
            points = sorted(points)
            if len(points) < n:
                continue

            lower = []
            for p in points:
                while len(lower) >= 2 and self.cross(lower[-2], lower[-1], p) <= 0:
                    lower.pop()
                lower.append(p)
            upper = []
            for p in reversed(points):
                while len(upper) >= 2 and self.cross(upper[-2], upper[-1], p) <= 0:
                    upper.pop()
                upper.append(p)
            convex = lower[:-1] + upper[:-1]

            # 严格凸检查
            if len(convex) >= n and self.is_strictly_convex(convex):
                convex = convex[:n]
                # 顺时针排序
                center = (sum(x for x, y in convex)/n, sum(y for x, y in convex)/n)
                convex.sort(key=lambda p: (-math.atan2(p[1]-center[1], p[0]-center[0]), p))
                return convex

    def is_strictly_convex(self, points):
        """检查多边形是否严格凸"""
        n = len(points)
        for i in range(n):
            a, b, c = points[i], points[(i+1)%n], points[(i+2)%n]
            if self.cross(a, b, c) == 0:
                return False
        return True

    def cross(self, o, a, b):
        return (a[0]-o[0])*(b[1]-o[1]) - (a[1]-o[1])*(b[0]-o[0])
