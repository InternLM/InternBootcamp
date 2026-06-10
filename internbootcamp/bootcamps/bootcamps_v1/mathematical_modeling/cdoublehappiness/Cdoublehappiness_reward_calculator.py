import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from math import isqrt




class CdoublehappinessRewardCalculator(BaseRewardCalculator):
    """Cdoublehappiness奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\]\s*(\d+)\s*\[/answer\]', output, re.IGNORECASE)
        if matches:
            try:
                return int(matches[-1])
            except ValueError:
                return None
        return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answer']
    
    # 其他额外方法

