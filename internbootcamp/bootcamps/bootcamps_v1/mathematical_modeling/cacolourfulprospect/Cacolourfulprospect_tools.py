import json
import logging
import os
from typing import Any, Optional, Tuple
from uuid import uuid4

from internbootcamp.src.base_tool import BaseTool
from verl.tools.schemas import OpenAIFunctionToolSchema
from verl.utils.rollout_trace import rollout_trace_op
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cacolourfulprospect.Cacolourfulprospect_reward_calculator import CacolourfulprospectRewardCalculator

# 导入依赖库
import math
import re
import random



logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))


class CacolourfulprospectVerificationTool(BaseTool):
    """Cacolourfulprospect验证工具"""
    
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
            score = CacolourfulprospectRewardCalculator.verify_score(
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
            logger.error(f"CacolourfulprospectVerificationTool执行错误: {str(e)}")
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
    def compute_regions(cls, n, circles):
        circles = [tuple(c) for c in circles]
        if n == 1:
            return 2
        if n == 2:
            return 2 + max(cls.ncut(*circles), 1)

        # 处理三个圆的情况
        c1, c2, c3 = circles
        cuts = (
            cls.ncut(c1, c2) 
            + cls.ncut(c2, c3) 
            + cls.ncut(c3, c1)
        )

        # 处理不相交圆对
        non_intersect_pairs = [
            (cls.ncut(c1, c2) == 0),
            (cls.ncut(c2, c3) == 0),
            (cls.ncut(c3, c1) == 0)
        ]
        if sum(non_intersect_pairs) >= 2:
            cuts += 1

        # 检测三圆公共交点
        if cuts >= 3 and cls.triple_intersection(circles):
            cuts -= 1
            if cls.collinear(c1[:2], c2[:2], c3[:2]):
                cuts -= 1

        return 2 + cuts

    @classmethod
    def ncut(cls, c1, c2):
        dx, dy = c1[0]-c2[0], c1[1]-c2[1]
        d_sq = dx**2 + dy**2
        r_sum = c1[2] + c2[2]
        r_diff = abs(c1[2] - c2[2])

        if d_sq > r_sum**2: return 0     # 外离
        if d_sq == r_sum**2: return 1    # 外切
        if d_sq < r_diff**2: return 0    # 内含
        if d_sq == r_diff**2: return 1   # 内切
        return 2                         # 相交

    @classmethod
    def triple_intersection(cls, circles):
        """精确检测三圆公共交点"""
        for i in range(3):
            a, b, c = circles[i], circles[(i+1)%3], circles[(i+2)%3]
            points = cls.get_intersections(a, b)
            for p in points:
                if cls.point_on_circle(p, c):
                    return True
        return False

    @staticmethod
    def get_intersections(c0, c1):
        """计算两圆精确交点"""
        x0, y0, r0 = c0
        x1, y1, r1 = c1

        d = math.hypot(x1-x0, y1-y0)
        if d > r0 + r1 or d < abs(r0 - r1):
            return []

        a = (r0**2 - r1**2 + d**2) / (2*d)
        h = math.sqrt(r0**2 - a**2)
        x2 = x0 + a*(x1 - x0)/d
        y2 = y0 + a*(y1 - y0)/d

        return [
            (x2 + h*(y1-y0)/d, y2 - h*(x1-x0)/d),
            (x2 - h*(y1-y0)/d, y2 + h*(x1-x0)/d)
        ] if h != 0 else [(x2, y2)]

    @staticmethod
    def point_on_circle(point, circle, eps=1e-8):
        """精确到1e-8的浮点误差判断"""
        x, y = point
        cx, cy, r = circle
        return abs((x - cx)**2 + (y - cy)**2 - r**2) < eps

    @staticmethod
    def collinear(p1, p2, p3):
        """三点共线检测优化版"""
        area = (p2[0] - p1[0])*(p3[1] - p1[1]) - (p2[1] - p1[1])*(p3[0] - p1[0])
        return abs(area) < 1e-8  # 允许浮点误差
