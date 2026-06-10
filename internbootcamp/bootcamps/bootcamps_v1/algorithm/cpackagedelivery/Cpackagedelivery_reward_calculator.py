import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

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


class CpackagedeliveryRewardCalculator(BaseRewardCalculator):
    """Cpackagedelivery奖励计算器"""
    
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
        try:
            d = identity['d']
            n = identity['n']
            stations = identity['stations']
            correct = compute_min_cost(d, n, len(stations), stations)
            return solution == correct
        except:
            return False
    
    # 其他额外方法

