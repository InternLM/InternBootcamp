from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.eoptimalpolygonperimeter.Eoptimalpolygonperimeter_reward_calculator import EoptimalpolygonperimeterRewardCalculator

# 导入依赖库
import re
import random
import math




class EoptimalpolygonperimeterInteraction(BaseInteraction):
    """Eoptimalpolygonperimeter交互管理器"""
    
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
        score = EoptimalpolygonperimeterRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Eoptimalpolygonperimeter问题！"""
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
