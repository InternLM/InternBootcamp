import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class CanniversaryRewardCalculator(BaseRewardCalculator):
    """Canniversary奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\s*\]\s*(-?\d+)\s*\[/answer\s*\]', output, re.IGNORECASE)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity['correct_answer']
        return solution % identity['m'] == expected
    
    # 其他额外方法

