import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import re
import random
from collections import deque




class EpropagatingtreeRewardCalculator(BaseRewardCalculator):
    """Epropagatingtree奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        answers = []
        matches = re.findall(r'\[answer\]\s*(-?\d+)\s*\[/answer\]', output, re.IGNORECASE)
        return list(map(int, matches)) if matches else None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        expected = identity.get('correct_outputs', [])
        return isinstance(solution, list) and solution == expected
    
    # 其他额外方法

