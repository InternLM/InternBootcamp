from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.algorithm.ccaptainmarmot.Ccaptainmarmot_reward_calculator import CcaptainmarmotRewardCalculator

# 导入依赖库
import math
import re
import random
from itertools import combinations




class CcaptainmarmotInteraction(BaseInteraction):
    """Ccaptainmarmot交互管理器"""
    
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
        score = CcaptainmarmotRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个Ccaptainmarmot问题！"""
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
    def _generate_regiment(self, solvable=True):
        """Generate a regiment that can be solvable or unsolvable"""
        regiment = []
        origin_map = []

        # 1. Generate base points configuration
        if solvable:
            # Generate valid square points
            d = random.randint(1, 5)
            square_points = [
                (d, 0), (0, d), (-d, 0), (0, -d)
            ]
            random.shuffle(square_points)
        else:
            # Generate invalid points (non-square)
            square_points = [
                (random.randint(-5, 5), random.randint(-5, 5))
                for _ in range(4)
            ]
            # Ensure at least 3 points are collinear
            square_points[-1] = self._create_collinear_point(square_points[:3])

        # 2. Generate origins for each mole
        if self.same_origin:
            common_origin = (random.randint(-10, 10), random.randint(-10, 10))
            origin_map = [common_origin]*4
        else:
            origin_map = [(random.randint(-10, 10), random.randint(-10, 10)) 
                         for _ in range(4)]

        # 3. Apply rotations and build moles
        for idx in range(4):
            x_base, y_base = square_points[idx]
            a, b = origin_map[idx]

            # Apply random rotations
            rotations = random.randint(0, self.max_rotation)
            cx, cy = x_base, y_base
            for _ in range(rotations):
                nx = a - (cy - b)
                ny = b + (cx - a)
                cx, cy = nx, ny

            regiment.append((cx, cy, a, b))

        return regiment

    def _create_collinear_point(self, points):
        """Create a collinear point to make square impossible"""
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]

        # Find vector for points 0->1 and 0->2
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x3 - x1
        dy2 = y3 - y1

        # Ensure collinearity
        if dx1 * dy2 == dx2 * dy1:
            # Points are collinear, create another collinear point
            t = random.uniform(1.5, 3)
            return (x1 + t*dx1, y1 + t*dy1)
        else:
            # Force fourth point to be collinear
            t = random.uniform(0.5, 2)
            return (x2 + t*(x3 - x2), y2 + t*(y3 - y2))

    @staticmethod
    def _is_valid_square(points):
        # Calculate all pairwise squared distances
        dists = []
        for (x1, y1), (x2, y2) in combinations(points, 2):
            dist_sq = (x2-x1)**2 + (y2-y1)**2
            dists.append(dist_sq)

        # Verify square properties: 2 distinct distances (sides and diagonals)
        dists.sort()
        return (
            len(dists) == 6 and
            dists[0] == dists[1] == dists[2] == dists[3] and  # 4 equal sides
            dists[4] == dists[5] and                          # 2 equal diagonals
            dists[4] == 2 * dists[0] and                      # Diagonal = side*sqrt(2)
            dists[0] > 0                                      # Non-degenerate
        )

    @classmethod
    def _verify_single_regiment(cls, answer, regiment):
        """Verify single regiment answer"""
        rotation_states = []
        for mole in regiment:
            x, y, a, b = mole
            states = []
            current_x, current_y = x, y
            states.append((current_x, current_y))
            for _ in range(3):
                current_x, current_y = a - (current_y - b), b + (current_x - a)
                states.append((current_x, current_y))
            rotation_states.append(states)

        min_rotations = None
        for r0 in range(4):
            for r1 in range(4):
                for r2 in range(4):
                    for r3 in range(4):
                        points = [
                            rotation_states[0][r0],
                            rotation_states[1][r1],
                            rotation_states[2][r2],
                            rotation_states[3][r3]
                        ]
                        if cls._is_valid_square(points):
                            total = r0 + r1 + r2 + r3
                            if min_rotations is None or total < min_rotations:
                                min_rotations = total

        correct = min_rotations if min_rotations is not None else -1
        return answer == correct
