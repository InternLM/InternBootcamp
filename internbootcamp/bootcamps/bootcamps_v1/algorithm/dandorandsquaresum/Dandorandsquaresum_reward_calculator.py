import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DandorandsquaresumRewardCalculator(BaseRewardCalculator):
    """Dandorandsquaresum奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        count = [0]*20
        for num in identity['a']:
            for i in range(20):
                count[i] += (num >> i) & 1
        
        sum_sq = 0
        bits = count.copy()
        for _ in range(identity['n']):
            a = 0
            for i in range(20):  # 严格按参考代码顺序（低位→高位）
                if bits[i]:
                    a |= (1 << i)
                    bits[i] -= 1
            sum_sq += a*a
        return solution == sum_sq
    
    # 其他额外方法

