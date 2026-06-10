import re
import json
import random
from typing import Dict, Any, Optional
from internbootcamp.src.base_instruction_generator import BaseInstructionGenerator

# 导入依赖库
import random
import re




class CroadtocinemaInstructionGenerator(BaseInstructionGenerator):
    """Croadtocinema Bootcamp指令生成器"""
    
    def __init__(self, **params):
        """
        初始化Croadtocinema指令生成器
        
        Args:
            
        """
        super().__init__()
        
        # 原始初始化逻辑
        self.params = params
    
    def case_generator(self):
        # 参数初始化
        s = self.params.get('s', random.randint(10, 1000))
        k = self.params.get('k', random.randint(1, min(10, s-2)))
        n = self.params.get('n', random.randint(3, 10))
        
        # 生成未排序的加油站位置
        gas_stations = []
        while len(gas_stations) < k:
            candidate = random.randint(1, s-1)
            if candidate not in gas_stations:
                gas_stations.append(candidate)
        random.shuffle(gas_stations)  # 模拟输入时的任意顺序

        # 计算最大间距（需排序处理）
        sorted_gas = sorted(gas_stations + [s])
        prev, max_gap = 0, 0
        segments = []
        for pos in sorted_gas:
            seg = pos - prev
            segments.append(seg)
            max_gap = max(max_gap, seg)
            prev = pos

        # 20%概率生成无解案例
        if random.random() < 0.2:
            case_type = random.choice(['capacity', 'time'])
            if case_type == 'capacity':
                # 所有车辆油量不足
                cars = [(random.randint(1, 100), random.randint(1, max_gap-1)) 
                        for _ in range(n)]
                t = random.randint(1, 2*10**9)
            else:
                # 存在油量足够车辆但时间不足
                vi = max_gap + random.randint(0, 100)
                time_needed = sum(seg*2 - min(seg, vi - seg) for seg in segments)
                cars = [(random.randint(1, 100), vi)] + \
                       [(random.randint(101, 200), random.randint(max_gap, max_gap+100)) 
                        for _ in range(n-1)]
                t = random.randint(1, time_needed-1)  # 确保时间不足
            return {
                'n': n, 'k': k, 's': s, 't': t,
                'cars': cars, 'gas_stations': gas_stations.copy(),
                '_sorted_gas': sorted_gas  # 内部记录排序后位置用于验证
            }

        # 生成有解案例
        min_price = random.randint(50, 200)
        valid_vi = max_gap + random.randint(0, 100)
        cars = [(min_price, valid_vi)]
        
        # 生成干扰车辆：价格更低（但油量不足）或价格更高（油量足够）
        for _ in range(n-1):
            if random.random() < 0.5:
                # 油量足够的高价车
                cars.append((min_price + random.randint(10, 100), valid_vi + random.randint(0, 50)))
            else:
                # 油量不足的低价车
                cars.append((random.randint(1, min_price-1), random.randint(1, max_gap-1)))
        random.shuffle(cars)
        
        # 计算合法最小时间
        t = sum(seg * 2 - min(seg, valid_vi - seg) for seg in segments)
        return {
            'n': n, 'k': k, 's': s, 't': t,
            'cars': cars, 'gas_stations': gas_stations.copy(),
            '_sorted_gas': sorted_gas  # 内部记录排序后位置用于验证
        }
    
    @staticmethod
    def prompt_func(case):
        input_data = '\n'.join([
            f"{case['n']} {case['k']} {case['s']} {case['t']}",
            *[f"{c} {v}" for c, v in case['cars']],
            ' '.join(map(str, case['gas_stations']))
        ])
        return f"""你需要帮助Vasya选择最便宜的汽车按时到达电影院。规则：
1. 油箱容量必须≥最大相邻加油站间距（含起点终点）
2. 两种驾驶模式：
   - 正常模式：1km/2分钟，耗油1L
   - 加速模式：1km/1分钟，耗油2L
3. 输出最低租金，无解输出-1

输入数据：
{input_data}

请将最终答案置于[answer]标签内，如：[answer]50[/answer]""" 
# + '\n在正式提交答案前你有少量机会调用工具进行答案验证。'
    

