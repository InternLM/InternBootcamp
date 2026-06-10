import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class FtokitsukazeandstrangerectangleRewardCalculator(BaseRewardCalculator):
    """Ftokitsukazeandstrangerectangle奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

