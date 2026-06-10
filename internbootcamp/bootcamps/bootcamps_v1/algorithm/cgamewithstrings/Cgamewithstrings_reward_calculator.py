import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import string
import re
from collections import defaultdict




class CgamewithstringsRewardCalculator(BaseRewardCalculator):
    """Cgamewithstrings奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return float(last_match)
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        strings = identity['strings']
        try:
            correct_value = cls.calculate_expected_value(strings)
        except:
            return False
        if correct_value is None:
            return False
        if solution is None:
            return False
        absolute_error = abs(solution - correct_value)
        if absolute_error <= 1e-9:
            return True
        relative_error = absolute_error / (abs(correct_value) + 1e-12)
        return relative_error <= 1e-9
    
    # 其他额外方法

