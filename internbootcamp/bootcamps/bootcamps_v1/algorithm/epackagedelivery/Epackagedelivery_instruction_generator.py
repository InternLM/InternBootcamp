import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

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


class EpackagedeliveryInstructionGenerator(BaseInstructionGenerator):
    """Epackagedelivery Bootcamp指令生成器"""
    
    def __init__(self, max_d=1000, max_n=100, max_m=100):
        """
        初始化Epackagedelivery指令生成器
        
        Args:
            max_d: 参数描述
            max_n: 参数描述
            max_m: 参数描述
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.max_d = max_d
        self.max_n = max_n
        self.max_m = max_m
    
    def case_generator(self):
        while True:
            d = random.randint(1, self.max_d)
            n = random.randint(1, d)
            m = random.randint(1, min(self.max_m, d-1))
            
            # Generate valid stations
            valid = False
            stations = []
            for _ in range(3):  # 最多尝试三次生成有效用例
                xi = []
                while len(xi) < m:
                    x = random.randint(1, d-1)
                    if x not in xi:
                        xi.append(x)
                xi.sort()
                pi = [random.randint(1, 1000) for _ in range(m)]
                stations = list(zip(xi, pi))
                
                # 检查有效性
                valid = True
                prev = 0
                for x, _ in stations:
                    if x - prev > n:
                        valid = False
                        break
                    prev = x
                if d - prev > n:
                    valid = False
                if valid:
                    break
            
            # 计算正确答案
            try:
                if not valid:
                    correct_output = -1
                else:
                    correct_output = compute_min_cost(d, n, stations)
                    # 交叉验证
                    sorted_stations = sorted(stations, key=lambda x:x[0])
                    prev = 0
                    for x, _ in sorted_stations:
                        if x - prev > n:
                            correct_output = -1
                            break
                        prev = x
                    if d - prev > n:
                        correct_output = -1
            except:
                correct_output = -1
            
            return {
                'd': d,
                'n': n,
                'm': m,
                'stations': stations,
                'correct_output': correct_output
            }
    
    @staticmethod
    def prompt_func(question_case):
        stations = sorted(question_case['stations'], key=lambda x: x[0])
        stations_str = '\n'.join([f"{x} {p}" for x, p in stations])
        return f"""Johnny需要从位置0驾驶到{question_case['d']}。卡车油箱容量为{question_case['n']}升，初始满油，每单位距离消耗1升。沿途的加油站坐标为：
{stations_str}

请计算完成运输的最低燃料成本，无法到达时输出-1。答案请包含在[answer]和[/answer]标记中。""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

