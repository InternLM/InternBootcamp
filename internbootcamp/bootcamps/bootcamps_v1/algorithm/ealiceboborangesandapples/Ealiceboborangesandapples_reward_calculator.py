import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import math
import re
import random




class EaliceboborangesandapplesRewardCalculator(BaseRewardCalculator):
    """Ealiceboborangesandapples奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answer_blocks = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not answer_blocks:
            return None
        solution = answer_blocks[-1].strip()
        
        if solution.lower() == 'impossible':
            return 'Impossible'
        
        if re.fullmatch(r'(([1-9]\d*[AB])+)', solution):
            return solution
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        x, y = identity['x'], identity['y']
        
        if solution == 'Impossible':
            return math.gcd(x, y) > 1
        
        decompressed = cls.decompress(solution)
        if not decompressed:
            return False
        
        return cls.validate_sequence(decompressed, x, y)
    
    # 其他额外方法

