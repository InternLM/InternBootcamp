import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CroadtocinemaRewardCalculator(BaseRewardCalculator):
    """Croadtocinema奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        try:
            return int(matches[-1].strip()) if matches else None
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, case):
        try:
            user_ans = int(solution)
        except:
            return False

        # 解析关键参数
        sorted_gas = case['_sorted_gas']
        segments = [sorted_gas[0]] + [sorted_gas[i]-sorted_gas[i-1] for i in range(1, len(sorted_gas))]
        max_gap = max(segments)
        valid_cars = []

        for price, capacity in case['cars']:
            if capacity < max_gap:
                continue
            # 计算最短时间
            total_time = 0
            for seg in segments:
                rem = capacity - seg
                if rem < 0:
                    total_time = float('inf')
                    break
                x = min(seg, rem)
                total_time += x + (seg - x)*2
            if total_time <= case['t']:
                valid_cars.append(price)
        
        correct_ans = min(valid_cars) if valid_cars else -1
        return user_ans == correct_ans
    
    # 其他额外方法

