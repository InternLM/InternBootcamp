import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def calculate_min_pixels(n, m, x, y, rows):
    # 转置行以获取各列
    cols = list(zip(*rows))
    u = [col.count('.') for col in cols]  # 每列改为白色所需的修改次数（即列中黑色像素数）
    v = [n - count for count in u]        # 每列改为黑色所需的修改次数（即列中白色像素数）
    
    a = [u[0]]  # 以白色结尾的段的最小修改次数
    b = [v[0]]  # 以黑色结尾的段的最小修改次数
    s = x - 1   # 段长度至少为x，因此需要保留前s个状态
    
    # 处理前x-1列
    for i in range(1, x):
        # 由于段长度必须>=x，此时只能继续延长当前颜色段
        a = [float('inf')] + [prev + u[i] for prev in a]
        b = [float('inf')] + [prev + v[i] for prev in b]
    
    # 处理x到min(y, m)-1列
    for i in range(x, min(y, m)):
        # 可以开始新的颜色段，此时需要取另一种颜色的最小值
        min_b = min(b[s:]) if b[s:] else float('inf')
        new_a = [min_b + u[i]] + [prev + u[i] for prev in a]
        min_a = min(a[s:]) if a[s:] else float('inf')
        new_b = [min_a + v[i]] + [prev + v[i] for prev in b]
        a, b = new_a, new_b
    
    # 处理剩下的列（当m > y时）
    for i in range(min(y, m), m):
        # 需要确保段长度不超过y，因此保留前y个状态
        min_b = min(b[s:]) if b[s:] else float('inf')
        new_a = [min_b + u[i]] + [prev + u[i] for prev in a[:-1]]  # 保留前y-1个状态
        min_a = min(a[s:]) if a[s:] else float('inf')
        new_b = [min_a + v[i]] + [prev + v[i] for prev in b[:-1]]
        a, b = new_a, new_b
    
    # 最后，取所有可能状态中的最小值
    valid_a = a[s:] if a[s:] else [float('inf')]
    valid_b = b[s:] if b[s:] else [float('inf')]
    return min(min(valid_a), min(valid_b))


class CbarcodeRewardCalculator(BaseRewardCalculator):
    """Cbarcode奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity.get('correct_answer', None)
    
    # 其他额外方法

