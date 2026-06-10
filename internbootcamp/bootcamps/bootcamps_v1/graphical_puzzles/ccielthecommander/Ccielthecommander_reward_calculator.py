import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import deque




class CcielthecommanderRewardCalculator(BaseRewardCalculator):
    """Ccielthecommander奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip().replace('\n', ' ')
        last_match = ' '.join(last_match.split())
        if last_match.upper() == "IMPOSSIBLE!":
            return "Impossible!"
        return last_match
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return cls.validate_solution(identity['n'], identity['edges'], solution)
    
    # 其他额外方法

