import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class BsifidandstrangesubsequencesRewardCalculator(BaseRewardCalculator):
    """Bsifidandstrangesubsequences奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\s*](.*?)\[/answer\s*]', output, re.DOTALL | re.IGNORECASE)
        if not matches:
            return None
        try:
            return int(matches[-1].strip())
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return isinstance(solution, int) and solution == identity['expected']
    
    # 其他额外方法

