import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class DpolylineInstructionGenerator(BaseInstructionGenerator):
    """Dpolyline Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Dpolyline指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        super().__init__(**params)
        self.x_range = params.get('x_range', (-10**9, 10**9))
        self.y_range = params.get('y_range', (-10**9, 10**9))
    
    def case_generator(self):
        # 主动生成覆盖所有逻辑分支的测试案例
        case_type = random.choice(['colinear', 'two_x', 'two_y', 'full'])
        
        while True:
            if case_type == 'colinear':
                # 三点水平或垂直线
                axis = random.choice(['x', 'y'])
                val = random.randint(*self.x_range if axis == 'x' else self.y_range)
                points = []
                for _ in range(3):
                    if axis == 'x':
                        x = val
                        y = random.randint(*self.y_range)
                    else:
                        y = val
                        x = random.randint(*self.x_range)
                    points.append([x, y])
                    while len(points) < 3 and any(p == points[-1] for p in points[:-1]):
                        points[-1][0 if axis == 'x' else 1] += 1  # 确保不重复
            
            elif case_type == 'two_x':
                # 两个相同x的情况
                x_common = random.randint(*self.x_range)
                x_diff = x_common
                while x_diff == x_common:
                    x_diff = random.randint(*self.x_range)
                    
                points = [
                    [x_common, random.randint(*self.y_range)],
                    [x_common, random.randint(*self.y_range)],
                    [x_diff, random.randint(*self.y_range)]
                ]
            
            elif case_type == 'two_y':
                # 两个相同y的情况
                y_common = random.randint(*self.y_range)
                y_diff = y_common
                while y_diff == y_common:
                    y_diff = random.randint(*self.y_range)
                    
                points = [
                    [random.randint(*self.x_range), y_common],
                    [random.randint(*self.x_range), y_common],
                    [random.randint(*self.x_range), y_diff]
                ]
            
            else:  # full case
                points = []
                for _ in range(3):
                    x = random.randint(*self.x_range)
                    y = random.randint(*self.y_range)
                    while [x, y] in points:
                        x += 1
                        y += 1
                    points.append([x, y])
            
            # 去重检查
            if len({tuple(p) for p in points}) == 3:
                return {'points': points}
    
    @staticmethod
    def prompt_func(question_case):
        points = question_case['points']
        return f"""在平面坐标系上有三个点：{"、".join(f"({x},{y})" for x,y in points)}
请构造仅由坐标轴平行线段组成的简单折线（无自交/自触）连接所有点，求最小线段数。

答案应为1到3之间的整数，放在[answer]标签内。例如：[answer]2[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

