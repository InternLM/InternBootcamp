import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re

# === 源文件中的全局函数 ===

def compute_min_cost(d, n, m, stations):
    sorted_stations = sorted(stations + [(d, 0)], key=lambda x: x[0])
    prev_pos = 0
    for x, _ in sorted_stations:
        if x - prev_pos > n:
            return -1
        prev_pos = x
    
    stack = []
    next_lower = [None] * len(sorted_stations)
    
    # Preprocess next_lower using monotonic stack
    for i in reversed(range(len(sorted_stations))):
        while stack and sorted_stations[stack[-1]][1] >= sorted_stations[i][1]:
            stack.pop()
        if stack:
            next_lower[i] = stack[-1]
        else:
            next_lower[i] = None
        stack.append(i)
    
    current_pos = 0
    current_fuel = n
    total_cost = 0
    
    for i, (x, p) in enumerate(sorted_stations):
        distance = x - current_pos
        current_fuel -= distance
        if current_fuel < 0:
            return -1
        current_pos = x
        
        if x == d:
            break
        
        j = next_lower[i]
        if j is None:
            max_reach = min(current_pos + n, d)
            buy = min(n - current_fuel, max_reach - x)
            if buy < 0:
                continue
            total_cost += buy * p
            current_fuel += buy
        else:
            max_reach = sorted_stations[j][0]
            required = max(0, (max_reach - x) - current_fuel)
            buy = min(required, n - current_fuel)
            total_cost += buy * p
            current_fuel += buy
        
        if current_fuel < 0:
            return -1
    
    return total_cost if current_pos == d else -1


class CpackagedeliveryInstructionGenerator(BaseInstructionGenerator):
    """Cpackagedelivery Bootcamp指令生成器"""
    
    def __init__(self, d_range=(5, 100), n_range=(2, 10), m_range=(1, 10)):
        """
        初始化Cpackagedelivery指令生成器
        
        Args:
            d_range: 参数描述
            n_range: 参数描述
            m_range: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.d_range = d_range
        self.n_range = n_range
        self.m_range = m_range

        min_d, max_d = self.d_range
        if min_d < 1 or max_d < 1:
            raise ValueError("d must be at least 1")
    
    def case_generator(self):
        d = random.randint(*self.d_range)
        n = random.randint(max(1, self.n_range[0]), min(d, self.n_range[1]))
        
        possible_xi = list(range(1, d))
        max_valid_m = len(possible_xi)
        min_m = max(self.m_range[0], 0)
        max_m = min(self.m_range[1], max_valid_m)
        m = random.randint(min_m, max_m) if max_m >= min_m else 0
        
        stations_xi = []
        if m > 0:
            stations_xi = random.sample(possible_xi, m)
            stations_xi.sort()
        stations_pi = [random.randint(1, 100) for _ in range(m)]
        
        return {
            'd': d,
            'n': n,
            'm': m,
            'stations': list(zip(stations_xi, stations_pi))
        }
    
    @staticmethod
    def prompt_func(question_case):
        d = question_case['d']
        n = question_case['n']
        m = question_case['m']
        stations = question_case['stations']
        stations_list = "\n".join([f"- 位置 {x}，价格 {p} 美元/升" for x, p in stations])
        return f"""Johnny需要驾驶卡车从0点前往{d}点，油箱容量{n}升。当前有{m}个加油站：
{stations_list}

请计算最小油费（无法到达时输出-1）。答案置于[answer]标签内，如：[answer]42[/answer]。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

