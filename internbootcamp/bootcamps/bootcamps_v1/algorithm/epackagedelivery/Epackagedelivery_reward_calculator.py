import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import heapq
import random
import re

# === 源文件中的全局函数 ===

def compute_min_cost(d, n, stations):
    stations = sorted(stations, key=lambda x: x[0])
    # Add start and end points
    stations = [(0, 0)] + stations + [(d, 0)]
    heap = []
    total_cost = 0
    current_fuel = n  # 初始满油
    prev_pos = 0
    
    for i in range(1, len(stations)):
        current_pos, price = stations[i]
        distance = current_pos - prev_pos
        
        # Consume fuel for this distance
        current_fuel -= distance
        
        # Need to refuel if current_fuel < 0
        while current_fuel < 0:
            if not heap:
                return -1
            # Get cheapest fuel station
            p, pos = heapq.heappop(heap)
            # Calculate maximum fuel can be taken from this station
            max_refuel = min(-current_fuel, n - (prev_pos - pos))
            total_cost += max_refuel * p
            current_fuel += max_refuel
        
        if current_fuel < 0:
            return -1
        
        # Add current station to heap
        if i < len(stations)-1:  # 终点不加入堆
            heapq.heappush(heap, (price, current_pos))
        prev_pos = current_pos
    
    return total_cost


class EpackagedeliveryRewardCalculator(BaseRewardCalculator):
    """Epackagedelivery奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](-?\d+)\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_output']
    
    # 其他额外方法

