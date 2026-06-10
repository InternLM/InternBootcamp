import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BplusandmultiplyRewardCalculator(BaseRewardCalculator):
    """Bplusandmultiply奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        last_match = matches[-1].strip().lower()
        return last_match.capitalize() if last_match in ('yes', 'no') else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        a = identity['a']
        b = identity['b']
        expected = 'Yes' if cls.check_in_set(n, a, b) else 'No'
        return solution.strip().lower() == expected.lower()
    
    # 其他额外方法

