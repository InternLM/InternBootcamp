import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from bisect import bisect_left
from bisect import bisect_right
import random
import re




class CthreebasestationsInstructionGenerator(BaseInstructionGenerator):
    """Cthreebasestations Bootcamp指令生成器"""
    
    def __init__(self, n_min=1, n_max=10**5, min_x=1, max_x=2*10**9):
        """
        初始化Cthreebasestations指令生成器
        
        Args:
            n_min: 参数描述
            n_max: 参数描述
            min_x: 参数描述
            max_x: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.n_min = max(n_min, 1)  # 确保n≥1
        self.n_max = n_max
        self.min_x = min_x
        self.max_x = max_x
    
    def case_generator(self):
        # 增加边界情况生成概率
        if random.random() < 0.2:
            n = random.choice([1, 2, 3, 10**5])
        else:
            n = random.randint(self.n_min, self.n_max)
        
        # 生成特殊案例
        if random.random() < 0.15:
            x = random.randint(self.min_x, self.max_x)
            houses = [x] * n  # 所有房屋同一坐标
        else:
            houses = [random.randint(self.min_x, self.max_x) for _ in range(n)]
        
        correct_d, stations = self._compute_solution(n, houses)
        return {
            'n': n,
            'houses': houses,
            'correct_d': correct_d,
            'correct_stations': stations
        }
    
    @staticmethod
    def prompt_func(question_case):
        houses = question_case['houses']
        return f"""The New Vasjuki village needs to install three base stations with equal power d. All houses must be covered by [t-d, t+d] ranges.

Input:
n = {question_case['n']}
House coordinates (unsorted): {' '.join(map(str, houses))}

Output format:
1. Minimal d with exactly 6 decimal places
2. Three station coordinates with exactly 6 decimal places

Put your final answer between [answer] and [/answer]. Example:
[answer]
0.500000
1.500000 2.500000 3.500000
[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def _compute_solution(n, houses):
        a = sorted([x * 2 for x in houses])
        if not a:
            return 0.0, [0.0, 0.0, 0.0]

        left, right = 0, 1 << 31

        # 二分查找最小d
        while left < right:
            mid = (left + right) // 2
            s = mid * 2
            x = bisect_right(a, a[0] + s)
            y = bisect_left(a, a[-1] - s)

            if x < y and (a[y-1] - a[x] > s):
                left = mid + 1
            else:
                right = mid

        d = left
        correct_d = d / 2.0

        # 计算基站坐标
        x_val = bisect_right(a, a[0] + d * 2)
        y_val = bisect_left(a, a[-1] - d * 2)

        # 处理全范围覆盖的情况
        if x_val >= len(a):
            return correct_d, [a[0]/2.0, a[0]/2.0, a[0]/2.0]

        # 计算三段分割点
        s1 = (a[0] + a[x_val-1])/4.0 if x_val > 0 else a[0]/2.0
        s2 = (a[x_val] + a[y_val-1])/4.0 if x_val < y_val else s1
        s3 = (a[y_val] + a[-1])/4.0 if y_val < len(a) else a[-1]/2.0

        return correct_d, [s1, s2, s3]
