import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
from bisect import bisect_left
from bisect import insort




class CtournamentRewardCalculator(BaseRewardCalculator):
    """Ctournament奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        import re
        matches = re.findall(r'\[answer\]\s*((?:\d+\s*)+)\[/answer\]', output)
        if not matches: return None
        try:
            return list(map(int, matches[-1].strip().split()))
        except:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['answers']
    
    # 其他额外方法

