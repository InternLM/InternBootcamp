import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from bisect import bisect_left
import re
import random
import math




class DdonkeyandstarsInstructionGenerator(BaseInstructionGenerator):
    """Ddonkeyandstars Bootcamp指令生成器"""
    
    def __init__(self, max_stars=10, min_param=1, max_param=5):
        """
        初始化Ddonkeyandstars指令生成器
        
        Args:
            max_stars: 参数描述
            min_param: 参数描述
            max_param: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        """
        参数:
            max_stars: 生成的最大星星数量
            min_param: 角度参数最小取值
            max_param: 角度参数最大取值
        """
        self.max_stars = max_stars
        self.min_param = min_param
        self.max_param = max_param
    
    def case_generator(self):
        """生成满足约束条件的有效案例"""
        a, b, c, d = self._generate_valid_angles()
        n = random.randint(5, self.max_stars)
        stars = self._generate_valid_stars(n, a, b, c, d)
        
        # 如果有效星星不足，重新生成
        while len(stars) < 3:
            a, b, c, d = self._generate_valid_angles()
            stars = self._generate_valid_stars(n, a, b, c, d)
        
        return {
            'n': len(stars),
            'alpha1': f"{a}/{b}",
            'alpha2': f"{c}/{d}",
            'stars_coordinates': stars,
            '_params': (a, b, c, d)  # 用于验证的内部参数
        }
    
    @staticmethod
    def prompt_func(question_case):
        alpha1 = question_case['alpha1']
        alpha2 = question_case['alpha2']
        n = question_case['n']
        stars = question_case['stars_coordinates']
        stars_lines = '\n'.join(f"{x} {y}" for x, y in stars)
        
        return f"""You are solving a geometric puzzle. Find the maximum star chain length following these rules:

1. Coordinate system has origin at chimney intersection
2. Initial rays make angles with OX where tan(α1) = {alpha1}, tan(α2) = {alpha2}
3. Each subsequent star must lie strictly between new rays from the previous star
4. Chain starts at origin (not counted)

Input format:
{n}
{alpha1} {alpha2}
{stars_lines}

Output the maximum chain length m. Put your answer between [answer] and [/answer] tags.

Example:
[answer]3[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _generate_valid_angles(self):
        """生成满足条件的角度参数: α1 < α2且tan值均为正"""
        while True:
            a, b = random.randint(self.min_param, self.max_param), random.randint(self.min_param, self.max_param)
            c, d = random.randint(self.min_param, self.max_param), random.randint(self.min_param, self.max_param)
            tan1 = a / b
            tan2 = c / d
            if tan1 < tan2 and tan1 > 0 and tan2 > 0:
                return (a, b, c, d)

    def _generate_valid_stars(self, n, a1, b1, c2, d2):
        """生成满足转换后坐标x>0,y>0的星星"""
        stars = []
        for _ in range(n*2):  # 生成冗余数据确保足够有效点
            x = random.randint(1, self.max_stars*2)
            y = random.randint(1, self.max_stars*2)
            # 计算转换后的坐标
            tx = c2 * x - d2 * y
            ty = b1 * y - a1 * x
            if tx > 0 and ty > 0:
                stars.append((x, y))
            if len(stars) >= n:
                break
        return stars[:n]
