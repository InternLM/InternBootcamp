from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.mathematical_modeling.cacolourfulprospect.Cacolourfulprospect_reward_calculator import CacolourfulprospectRewardCalculator

# 导入依赖库
import math
import re
import random




class CacolourfulprospectInteraction(BaseInteraction):
    """Cacolourfulprospect交互管理器"""
    
    def __init__(self, config: dict[str, Any]):
        super().__init__(config)

    async def start_interaction(self, instance_id: Optional[str] = None, identity: dict[str, Any] = None, **kwargs) -> str:
        """开始交互会话"""
        return await super().start_interaction(instance_id, identity, **kwargs)

    async def generate_response(self, instance_id: str, messages: list[dict[str, Any]], **kwargs) -> tuple[bool, str, float, dict[str, Any]]:
        """
        生成交互反馈响应
        
        Args:
            instance_id: 实例ID
            messages: 对话历史消息列表
            
        Returns:
            should_terminate_sequence: 是否终止交互序列
            response_content: 反馈内容
            current_turn_score: 当前轮次得分
            additional_data: 额外数据
        """
        # 获取最近的assistant消息
        assistant_content = ""
        for i in range(len(messages) - 1, -1, -1):
            item = messages[i]
            if item.get("role") == "assistant":
                assistant_content = item.get("content", "")
                break
        
        if not assistant_content:
            return False, "请提供你的解决方案。", 0.0, {}
        
        # 使用奖励计算器评估解决方案
        identity = self._instance_dict[instance_id]['identity']
        score = CacolourfulprospectRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Cacolourfulprospect问题！"""
            should_terminate = True
            
        elif score > 0.0:
            response = f"""⚠️ 你的解决方案部分正确（得分: {score:.2f}/1.0），但仍有一些问题需要解决。

请检查并修正你的解决方案。"""
            should_terminate = False
            
        else:
            response = f"""❌ 你的解决方案存在错误（得分: {score:.2f}/1.0）。

请重新思考并提供新的解决方案。"""
            should_terminate = False
        
        return should_terminate, response, score, {}

    async def calculate_score(self, instance_id: str, **kwargs) -> float:
        """计算交互得分"""
        return await super().calculate_score(instance_id, **kwargs)

    async def finalize_interaction(self, instance_id: str, **kwargs) -> bool:
        """结束交互并释放资源"""
        return await super().finalize_interaction(instance_id, **kwargs)
    
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
