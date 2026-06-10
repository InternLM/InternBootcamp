import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from bisect import bisect_left
from bisect import bisect_right
import random
import re




class CthreebasestationsRewardCalculator(BaseRewardCalculator):
    """Cthreebasestations奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        # 提取最后一个答案块
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        
        content = answer_blocks[-1].strip().split('\n')
        if len(content) < 2:
            return None
        
        try:
            d = round(float(content[0].strip()), 6)
            stations = [round(float(x.strip()), 6) for x in content[1].split()]
            if len(stations) != 3:
                return None
            return {'d': d, 'stations': stations}
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution or 'd' not in solution or 'stations' not in solution:
            return False
        
        solution_d = solution['d']
        epsilon = 1e-7  # 扩大容差范围
        
        # 验证d值精度
        if abs(solution_d - identity['correct_d']) > epsilon:
            return False
        
        # 验证所有房屋被覆盖
        stations = solution['stations']
        for house in identity['houses']:
            if not any(
                (house >= (s - solution_d - epsilon)) and 
                (house <= (s + solution_d + epsilon))
                for s in stations
            ):
                return False
        
        return True
    
    # 其他额外方法

