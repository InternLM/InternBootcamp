import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random




class BzumaRewardCalculator(BaseRewardCalculator):
    """Bzuma奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        numbers = re.findall(r'-?\d+', last_match)
        return int(numbers[-1]) if numbers else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not isinstance(solution, int) or solution < 1:
            return False
        return solution == identity['min_steps']
    
    # 其他额外方法

