import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random

# === 源文件中的全局函数 ===

def calculate_answer(points):
    if not points:
        return 0
    
    # 离散化坐标
    x_coords = sorted({x for x, y in points})
    y_coords = sorted({y for x, y in points})
    
    x_map = {x: i for i, x in enumerate(x_coords)}
    y_map = {y: i for i, y in enumerate(y_coords)}
    
    # 按y分层存储x坐标
    y_buckets = [[] for _ in range(len(y_coords))]
    for x, y in points:
        y_idx = y_map[y]
        y_buckets[y_idx].append(x_map[x])
    
    for bucket in y_buckets:
        bucket.sort()
    
    total = 0
    st = SegmentTree(len(x_coords))
    
    # 按y降序处理
    for bucket in reversed(y_buckets):
        # 添加当前层的点
        for x in bucket:
            if st.query_range(x, x+1) == 0:
                st.update(x, 1)
        
        prev_x = -1
        for x in bucket:
            # 计算左区域贡献
            left = st.query_range(prev_x + 1, x + 1)
            # 计算右区域贡献（包括无穷大情况）
            right = st.query_range(x + 1, len(x_coords)) + 1
            total += left * right
            prev_x = x
    
    return total



# === 源文件中的其他类 ===

class SegmentTree:
    def __init__(self, size):
        self.m = 1
        while self.m < size:
            self.m <<= 1
        self.data = [0] * (2 * self.m)
    
    def update(self, index, value):
        index += self.m
        while index > 0:
            self.data[index] += value
            index >>= 1
    
    def query_range(self, l, r):
        res = 0
        l += self.m
        r += self.m
        while l < r:
            if l % 2 == 1:
                res += self.data[l]
                l += 1
            if r % 2 == 1:
                r -= 1
                res += self.data[r]
            l >>= 1
            r >>= 1
        return res


class FtokitsukazeandstrangerectangleInstructionGenerator(BaseInstructionGenerator):
    """Ftokitsukazeandstrangerectangle Bootcamp指令生成器"""
    
    def __init__(self, min_n=1, max_n=10, x_max=100, y_max=100):
        """
        初始化Ftokitsukazeandstrangerectangle指令生成器
        
        Args:
            min_n: 参数描述
            max_n: 参数描述
            x_max: 参数描述
            y_max: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.min_n = min_n
        self.max_n = max_n
        self.x_max = x_max
        self.y_max = y_max
    
    def case_generator(self):
        n = random.randint(self.min_n, self.max_n)
        points = set()
        while len(points) < n:
            x = random.randint(1, self.x_max)
            y = random.randint(1, self.y_max)
            points.add((x, y))
        points = list(points)
        answer = calculate_answer(points)
        return {
            'n': n,
            'points': points,
            'answer': answer
        }
    
    @staticmethod
    def prompt_func(question_case):
        points = question_case['points']
        n = question_case['n']
        input_lines = [f"{x} {y}" for x, y in points]
        input_str = '\n'.join([str(n)] + input_lines)
        return f"""请解决以下几何谜题，输出最终答案的数值。

题目描述：
平面上有{n}个互不相同的点。定义一个特殊矩形区域：由三条直线x=l（左边界）、x=r（右边界，满足l<r）和y=a（底边界）围成，顶部无限延伸。点(x_i, y_i)位于区域内当且仅当l < x_i < r且y_i > a。求可以形成的不同非空点集的数量。

输入格式：
第一行：n
接下来n行：每行两个整数x_i y_i

输入数据：
{input_str}

请将答案数值置于[answer]标签内，例如：[answer]42[/answer]。确保结果为整数。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

