import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
from math import hypot
import bisect
import random
import re




class DbuildingbridgeInstructionGenerator(BaseInstructionGenerator):
    """Dbuildingbridge Bootcamp指令生成器"""
    
    def __init__(self, a_range=(1, 1000), b_shift_range=(1, 1000), n_range=(1, 5), m_range=(1, 5), y_range=(-1000, 1000)):
        """
        初始化Dbuildingbridge指令生成器
        
        Args:
            a_range: 参数描述
            b_shift_range: 参数描述
            n_range: 参数描述
            m_range: 参数描述
            y_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.a_min, self.a_max = a_range
        self.b_shift_min, self.b_shift_max = b_shift_range
        self.n_range = n_range
        self.m_range = m_range
        self.y_min, self.y_max = y_range
    
    def case_generator(self):
        # 生成满足 0 < a < b <1e6 的整数坐标
        a = random.randint(self.a_min, self.a_max)
        b = a + random.randint(self.b_shift_min, self.b_shift_max)
        while b >= 1e6:
            a = random.randint(1, 999_999)
            b = a + random.randint(1, 999_999 - a)
        
        # 生成西岸点 (已排序的n个唯一整数)
        west_ys = sorted(random.sample(
            range(self.y_min, self.y_max+1),
            random.randint(*self.n_range)
        ))
        
        # 生成东岸点 (已排序的m个唯一整数)
        east_ys = sorted(random.sample(
            range(self.y_min, self.y_max+1),
            random.randint(*self.m_range)
        ))
        
        # 生成保证条件的l_list
        cx = random.randint(b + 1, 1_000_000)  # 东岸村庄x坐标
        cy = random.randint(-1_000_000, 1_000_000)
        l_list = []
        for y in east_ys:
            min_dist = hypot(cx - b, cy - y)
            lj = random.randint(
                max(1, int(min_dist)), 
                max(2, int(min_dist) + 1000)
            )
            l_list.append(lj)
        
        # 计算最优解
        solution, min_total = self.compute_optimal_solution(
            a, b, west_ys, east_ys, l_list
        )
        
        return {
            'n': len(west_ys),
            'm': len(east_ys),
            'a': a,
            'b': b,
            'west_ys': west_ys,
            'east_ys': east_ys,
            'l_list': l_list,
            'solution': solution,
            'min_total': min_total
        }
    
    @staticmethod
    def prompt_func(case):
        question = [
            "Two villages are separated by a river at x={} (west) and x={} (east).".format(case['a'], case['b']),
            "West village paths end at y coordinates (sorted): " + ', '.join(map(str, case['west_ys'])),
            "East village paths end at y coordinates (sorted): " + ', '.join(map(str, case['east_ys'])),
            "East path lengths: " + ', '.join(map(str, case['l_list'])),
            "Find the 1-based indices of optimal west and east points.",
            "Put your answer between [answer] and [/answer], e.g.: [answer]2 3[/answer]"
        ]
        return '\n'.join(question) 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    
    @staticmethod
    def compute_optimal_solution(a, b, west_ys, east_ys, l_list):
        delta = b - a
        min_total = float('inf')
        best_pair = (-1, -1)

        # 预处理西岸点的索引映射 (输入已排序，索引即为1-based编号)
        indexed_west = list(enumerate(west_ys, 1))

        for east_idx, (bj_y, lj) in enumerate(zip(east_ys, l_list), 1):
            # 计算最佳西岸匹配点
            target_y = (bj_y * a) / b
            pos = bisect.bisect_left(west_ys, target_y)

            # 检查候选窗口
            candidates = set()
            for offset in (-1, 0, 1):
                k = pos + offset
                if 0 <= k < len(west_ys):
                    candidates.add(k)

            # 遍历所有候选点
            for k in candidates:
                ai_y = west_ys[k]
                total = (
                    hypot(a, ai_y) +          # OAi
                    hypot(delta, bj_y - ai_y) + # AiBj
                    lj                        # lj
                )
                if total < min_total:
                    min_total = total
                    best_pair = (k+1, east_idx)  # 转换为1-based索引

        return best_pair, min_total
