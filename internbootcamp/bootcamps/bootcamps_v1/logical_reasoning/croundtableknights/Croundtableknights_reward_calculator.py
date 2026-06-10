import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class CroundtableknightsRewardCalculator(BaseRewardCalculator):
    """Croundtableknights奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](YES|NO)\[/answer\]', output, re.IGNORECASE)
        return matches[-1].strip().upper() if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        correct = 'YES' if cls._is_lucky(identity['n'], identity['status']) else 'NO'
        return (solution or '').upper() == correct
    
    # 其他额外方法

