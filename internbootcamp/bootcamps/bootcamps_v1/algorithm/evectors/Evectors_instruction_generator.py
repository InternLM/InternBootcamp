import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EvectorsInstructionGenerator(BaseInstructionGenerator):
    """Evectors Bootcamp指令生成器"""
    
    def __init__(self, max_coordinate: int = 10**3):
        """
        初始化Evectors指令生成器
        
        Args:
            max_coordinate: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_coord = max_coordinate
    
    def case_generator(self) -> Dict:
        generators = [
            self._gen_solvable_case,
            self._gen_unsolvable_zeroC,
            self._gen_unsolvable_general
        ]
        return random.choice(generators)()
    
    @staticmethod
    def prompt_func(case: Dict) -> str:
        a = case['A']
        b = case['B']
        c = case['C']
        return f"""给定初始向量A({a[0]}, {a[1]})，目标向量B({b[0]}, {b[1]})，操作向量C({c[0]}, {c[1]})。允许的操作：
1. 顺时针旋转90度（次数不限）
2. 累加向量C（次数不限）
请判断是否可以转换，并将最终答案用[answer]标签包裹，例如：[answer]YES[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    def _gen_solvable_case(self) -> Dict:
        """生成保证可解的案例"""
        ax = random.randint(-self.max_coord, self.max_coord)
        ay = random.randint(-self.max_coord, self.max_coord)
        p = random.randint(-self.max_coord, self.max_coord)
        q = random.randint(-self.max_coord, self.max_coord)

        # 随机选择旋转次数和系数
        rot = random.randint(0, 3)
        a = random.randint(-5, 5)
        b = random.randint(-5, 5)

        # 构造合法B向量
        rx, ry = rotate_clockwise(ax, ay, rot)
        bx = rx + a*p + b*q
        by = ry + a*q - b*p
        return {'A': [ax, ay], 'B': [bx, by], 'C': [p, q]}

    def _gen_unsolvable_zeroC(self) -> Dict:
        """生成C=0时的不可解案例"""
        ax = random.randint(-self.max_coord, self.max_coord)
        ay = random.randint(-self.max_coord, self.max_coord)
        p = q = 0

        # 寻找不在旋转对称点上的B
        while True:
            bx = random.randint(-self.max_coord, self.max_coord)
            by = random.randint(-self.max_coord, self.max_coord)
            if not any((bx, by) == rotate_clockwise(ax, ay, r) for r in range(4)):
                return {'A': [ax, ay], 'B': [bx, by], 'C': [p, q]}

    def _gen_unsolvable_general(self) -> Dict:
        """生成普通不可解案例"""
        for _ in range(100):
            case = self._gen_solvable_case()
            ax, ay = case['A']
            bx, by = case['B']
            p, q = case['C']

            # 微调B向量破坏可解性
            delta = random.choice([(1,0), (-1,0), (0,1), (0,-1)])
            new_bx = bx + delta[0]
            new_by = by + delta[1]
            if not is_possible(ax, ay, new_bx, new_by, p, q):
                return {'A': [ax, ay], 'B': [new_bx, new_by], 'C': [p, q]}
        return {'A': [0,0], 'B': [1,0], 'C': [0,0]}  # 最终后备案例
