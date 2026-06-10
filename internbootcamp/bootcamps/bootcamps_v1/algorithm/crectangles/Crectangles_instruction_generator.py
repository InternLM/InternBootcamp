import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CrectanglesInstructionGenerator(BaseInstructionGenerator):
    """Crectangles Bootcamp指令生成器"""
    
    def __init__(self, min_n=2, max_n=10, coord_range=(-100, 100)):
        """
        初始化Crectangles指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            coord_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.coord_range = coord_range
        # 保证公共点生成在中间区域，确保有空间生成不包含的矩形
        self.safe_coord_range = (coord_range[0] + 10, coord_range[1] - 10)
    
    def case_generator(self):
        """生成保证至少有n-1个矩形交于一点的案例"""
        n = random.randint(self.min_n, self.max_n)
        # 生成公共点（确保不在边界附近）
        x = random.randint(*self.safe_coord_range)
        y = random.randint(*self.safe_coord_range)
        
        rectangles = []
        # 生成前n-1个必然包含公共点的矩形
        for _ in range(n-1):
            x1 = random.randint(self.coord_range[0], x)
            x2 = random.randint(x, self.coord_range[1])
            x1, x2 = sorted([x1, x2])
            # 确保公共点在矩形边界内
            x1 = min(x1, x)
            x2 = max(x2, x)

            y1 = random.randint(self.coord_range[0], y)
            y2 = random.randint(y, self.coord_range[1])
            y1, y2 = sorted([y1, y2])
            y1 = min(y1, y)
            y2 = max(y2, y)
            
            rectangles.append([x1, y1, x2, y2])

        # 生成第n个矩形（可能包含或不包含公共点）
        if random.choice([True, False]):
            # 包含公共点的正常矩形
            x1 = random.randint(self.coord_range[0], x)
            x2 = random.randint(x, self.coord_range[1])
            x1, x2 = sorted([x1, x2])
            x1 = min(x1, x)
            x2 = max(x2, x)

            y1 = random.randint(self.coord_range[0], y)
            y2 = random.randint(y, self.coord_range[1])
            y1, y2 = sorted([y1, y2])
            y1 = min(y1, y)
            y2 = max(y2, y)
        else:
            # 不包含公共点的矩形（确保严格不包含）
            axis = random.choice(['x', 'y'])
            
            # 确保生成有效范围
            if axis == 'x':
                # x轴方向不包含
                direction = random.choice(['left', 'right'])
                if direction == 'left':
                    x_max = x - 1
                    x1 = random.randint(self.coord_range[0], x_max-1)
                    x2 = random.randint(x1+1, x_max)
                else:
                    x_min = x + 1
                    x1 = random.randint(x_min, self.coord_range[1]-1)
                    x2 = random.randint(x1+1, self.coord_range[1])
                # y轴随机生成
                y1 = random.randint(self.coord_range[0], self.coord_range[1]-1)
                y2 = random.randint(y1+1, self.coord_range[1])
            else:
                # y轴方向不包含
                direction = random.choice(['below', 'above'])
                if direction == 'below':
                    y_max = y - 1
                    y1 = random.randint(self.coord_range[0], y_max-1)
                    y2 = random.randint(y1+1, y_max)
                else:
                    y_min = y + 1
                    y1 = random.randint(y_min, self.coord_range[1]-1)
                    y2 = random.randint(y1+1, self.coord_range[1])
                # x轴随机生成
                x1 = random.randint(self.coord_range[0], self.coord_range[1]-1)
                x2 = random.randint(x1+1, self.coord_range[1])
                
            # 二次验证不包含
            assert not (x1 <= x <= x2 and y1 <= y <= y2), "生成错误：矩形包含公共点"
            
        rectangles.append([x1, y1, x2, y2])
        return {'n': n, 'rectangles': rectangles}
    
    @staticmethod
    def prompt_func(question_case) -> str:
        n = question_case['n']
        rects = question_case['rectangles']
        problem = f"""给定平面上的{n}个矩形，其中至少{n-1}个有共同点。找到任意属于至少{n-1}个矩形的整数坐标点。

输入格式：
第一行：{n}
接下来{n}行，每行四个整数：x1 y1 x2 y2

具体输入：
{n}
""" + '\n'.join(' '.join(map(str, r)) for r in rects) + """

输出要求：
两个整数x y，用空格分隔，放置在[answer]标签内

示例答案：
[answer]42 314[/answer]"""
        return problem 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

