import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from typing import Dict
from typing import List

# === 源文件中的全局函数 ===

def rotate_clockwise(x: int, y: int, times: int) -> (int, int):
    """顺时针旋转向量，times为旋转次数"""
    for _ in range(times % 4):
        x, y = y, -x
    return x, y

def possible(dx: int, dy: int, p: int, q: int) -> bool:
    """验证差分向量是否符合线性组合条件"""
    bm = p**2 + q**2
    if bm == 0:
        return dx == 0 and dy == 0
    return ((-p*dx - q*dy) % bm == 0) and ((-q*dx + p*dy) % bm == 0)

def is_possible(ax: int, ay: int, bx: int, by: int, p: int, q: int) -> bool:
    """验证所有旋转可能性"""
    for rot in range(4):
        rx, ry = rotate_clockwise(ax, ay, rot)
        dx, dy = bx - rx, by - ry
        if possible(dx, dy, p, q) or possible(-dy, dx, p, q):
            return True
    return False


class EvectorsRewardCalculator(BaseRewardCalculator):
    """Evectors奖励计算器"""
    
    @staticmethod
    def extract_output(output: str) -> str:
        matches = re.findall(r'\[answer\]\s*(YES|NO)\s*\[/answer\]', output, re.IGNORECASE)
        return matches[-1].upper() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution: str, identity: Dict) -> bool:
        ax, ay = identity['A']
        bx, by = identity['B']
        p, q = identity['C']
        expected = 'YES' if is_possible(ax, ay, bx, by, p, q) else 'NO'
        return solution.upper() == expected
    
    # 其他额外方法

