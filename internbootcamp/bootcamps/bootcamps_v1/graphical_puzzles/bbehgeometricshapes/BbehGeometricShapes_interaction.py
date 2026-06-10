from typing import Any, Optional

from internbootcamp.src.base_interaction import BaseInteraction
from internbootcamp.bootcamps.bootcamps_v1.graphical_puzzles.bbehgeometricshapes.BbehGeometricShapes_reward_calculator import BbehgeometricshapesRewardCalculator

# 导入依赖库
import random
import re
import random
import math
import json
import matplotlib.pyplot as plt

# === 源文件中的全局函数 ===

def generate_rectangle():
    x = random.uniform(0, 50)
    y = random.uniform(0, 50)
    width = random.uniform(10, 30)
    height = random.uniform(10, 30)
    while abs(width - height) < 5:  # Ensure not square
        height = random.uniform(10, 30)
    return [
        (x, y),
        (x + width, y),
        (x + width, y + height),
        (x, y + height),
        (x, y)
    ]

def generate_square():
    x = random.uniform(0, 50)
    y = random.uniform(0, 50)
    size = random.uniform(10, 30)
    return [
        (x, y),
        (x + size, y),
        (x + size, y + size),
        (x, y + size),
        (x, y)
    ]

def generate_parallelogram():
    x = random.uniform(0, 50)
    y = random.uniform(0, 50)
    width = random.uniform(10, 30)
    height = random.uniform(10, 30)
    skew = random.uniform(5, 15)
    if random.random() < 0.5:
        skew = -skew
    if random.random() < 0.5:
        return [
            (x, y),
            (x + width + skew, y),
            (x + width, y + height),
            (x - skew, y + height),
            (x, y)
        ]
    else:
        return [
            (x, y),
            (x, y + width + skew),
            (x + height, y + width),
            (x + height, y - skew),
            (x, y)
        ]

def generate_triangle(non_right=True):
    if non_right:
        # Generate non-right triangle
        a = (random.uniform(0, 50), random.uniform(0, 50))
        b = (a[0] + random.uniform(10, 30), a[1])
        c = (a[0] + random.uniform(5, 15), a[1] + random.uniform(10, 30))
        # Check if right triangle
        v1 = (b[0]-a[0], b[1]-a[1])
        v2 = (c[0]-a[0], c[1]-a[1])
        if abs(v1[0]*v2[0] + v1[1]*v2[1]) < 1e-6:
            c = (c[0]+5, c[1])
        return [a, b, c, a]
    else:
        # Generate right triangle with random right angle vertex
        right_angle_at = random.choice(['a', 'b', 'c'])
        if right_angle_at == 'a':
            a = (random.uniform(-20, 70), random.uniform(-20, 70))
            dx = random.uniform(10, 30) * random.choice([1, -1])
            dy = random.uniform(10, 30) * random.choice([1, -1])
            b = (a[0] + dx, a[1])
            c = (a[0], a[1] + dy)
        elif right_angle_at == 'b':
            b = (random.uniform(-20, 70), random.uniform(-20, 70))
            dx = random.uniform(10, 30) * random.choice([1, -1])
            dy = random.uniform(10, 30) * random.choice([1, -1])
            a = (b[0] - dx, b[1])
            c = (b[0], b[1] + dy)
        else:  # right_angle_at == 'c'
            c = (random.uniform(-20, 70), random.uniform(-20, 70))
            dx = random.uniform(10, 30) * random.choice([1, -1])
            dy = random.uniform(10, 30) * random.choice([1, -1])
            a = (c[0] - dx, c[1])
            b = (c[0], c[1] - dy)
        return [a, b, c, a]

def generate_trapezoid():
    x = random.uniform(0, 50)
    y = random.uniform(0, 50)
    base1 = random.uniform(20, 40)
    base2 = base1 * random.uniform(0.3, 0.7)  # Ensure different lengths
    height = random.uniform(15, 30)
    offset = (base1 - base2) * random.uniform(0.4, 0.6)
    if random.random() < 0.5:
        x,y = y,x
    if random.random() < 0.5:
        return [
            (x, y),
            (x + base1, y),
            (x + base1 - offset, y + height),
            (x + offset, y + height),
            (x, y)
        ]
    else:
        return [
            (x, y),
            (x, y + base1),
            (x + height, y + base1 - offset),
            (x + height, y + offset),
            (x, y)
        ]

def generate_regular_polygon(sides, size=30):
    points = []
    # 固定半径（保证边长相等）
    radius = size * random.uniform(0.8, 1.2)  # 整体缩放
    start_angle = random.uniform(0, 2*math.pi)  # 随机旋转
    center_x = random.uniform(20, 80)  # 随机中心点
    center_y = random.uniform(20, 80)
    
    for i in range(sides):
        angle = 2 * math.pi * i / sides + start_angle
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        points.append((x, y))
    points.append(points[0])  # 闭合路径
    return points

def generate_irregular_convex_pentagon():
    angles = [i*72 + random.uniform(-15, 15) for i in range(5)]
    points = []
    for angle in angles:
        r = random.uniform(20, 35)
        x = 50 + r * math.cos(math.radians(angle))
        y = 50 + r * math.sin(math.radians(angle))
        points.append((x, y))
    points.append(points[0])
    return points

def generate_irregular_concave_pentagon():
    convex = generate_irregular_convex_pentagon()[:-1]
    # Create concave by moving one point inward
    idx = random.randint(0, 4)
    centroid_x = sum(p[0] for p in convex)/5
    centroid_y = sum(p[1] for p in convex)/5
    # Move towards centroid with overshoot
    new_x = convex[idx][0] + 1.5*(centroid_x - convex[idx][0])
    new_y = convex[idx][1] + 1.5*(centroid_y - convex[idx][1])
    convex[idx] = (new_x, new_y)
    convex.append(convex[0])
    return convex

def split_segment(a, b, num_splits=1):
    points = [a]
    for _ in range(num_splits):
        t = random.uniform(0.2, 0.8)
        x = a[0] + t*(b[0]-a[0])
        y = a[1] + t*(b[1]-a[1])
        points.append((x, y))
    points.append(b)
    return points

def last_boxed_only_string(string):
    idx = string.rfind("\\boxed")
    if "\\boxed " in string:
        return "\\boxed " + string.split("\\boxed ")[-1].split("$")[0]
    if idx < 0:
        idx = string.rfind("\\fbox")
        if idx < 0:
            return None

    i = idx
    right_brace_idx = None
    num_left_braces_open = 0
    while i < len(string):
        if string[i] == "{":
            num_left_braces_open += 1
        if string[i] == "}":
            num_left_braces_open -= 1
            if num_left_braces_open == 0:
                right_brace_idx = i
                break
        i += 1

    if right_brace_idx is None:
        retval = None
    else:
        retval = string[idx:right_brace_idx + 1]

    return retval

def remove_boxed(s):
    if "\\boxed " in s:
        left = "\\boxed "
        assert s[:len(left)] == left
        return s[len(left):]

    left = "\\boxed{"

    assert s[:len(left)] == left
    assert s[-1] == "}"

    return s[len(left):-1]


class BbehgeometricshapesInteraction(BaseInteraction):
    """Bbehgeometricshapes交互管理器"""
    
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
        score = BbehgeometricshapesRewardCalculator.verify_score(
            model_output=assistant_content, 
            identity=identity
        )
        
        # 根据得分生成相应的反馈
        if score == 1.0:
            response = """🎉 恭喜！你的解决方案完全正确！
            
你已经成功解决了这个BbehGeometricShapes问题！"""
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

