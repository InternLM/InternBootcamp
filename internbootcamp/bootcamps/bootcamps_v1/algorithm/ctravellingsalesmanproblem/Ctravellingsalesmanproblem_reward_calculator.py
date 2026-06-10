import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from heapq import heappush
from heapq import heappop
import random
import re




class CtravellingsalesmanproblemRewardCalculator(BaseRewardCalculator):
    """Ctravellingsalesmanproblem奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\][^\d]*(-?\d+)[^\d]*\[/answer\]', output)
        return int(matches[-1]) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        return solution == identity['correct_answer']
    
    # 其他额外方法

