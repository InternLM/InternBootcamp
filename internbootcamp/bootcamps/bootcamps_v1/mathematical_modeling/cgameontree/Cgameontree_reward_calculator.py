import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CgameontreeRewardCalculator(BaseRewardCalculator):
    """Cgameontree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        try:
            return float(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if solution is None:
            return False
            
        expected = identity['expected']
        
        # Handle near-zero expected values
        if abs(expected) < 1e-12:
            return abs(solution) < 1e-6
        
        abs_error = abs(solution - expected)
        rel_error = abs_error / abs(expected)
        
        return abs_error <= 1e-6 or rel_error <= 1e-6
    
    # 其他额外方法

