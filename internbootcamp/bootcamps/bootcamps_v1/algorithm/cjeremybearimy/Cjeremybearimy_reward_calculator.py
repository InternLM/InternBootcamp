import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
from collections import defaultdict
from collections import deque
import random
import re




class CjeremybearimyRewardCalculator(BaseRewardCalculator):
    """Cjeremybearimy奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = re.sub(r'\s+', ' ', matches[-1]).strip()
        parts = last_match.split()
        if len(parts) != 2:
            return None
        try:
            return f"{int(parts[0])} {int(parts[1])}"
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        if not solution:
            return False
        parts = solution.split()
        if len(parts) != 2:
            return False
        try:
            sol_g, sol_b = map(int, parts)
        except ValueError:
            return False

        correct_g, correct_b = cls.calculate_GB(identity['k'], identity['edges'])
        return sol_g == correct_g and sol_b == correct_b
    
    # 其他额外方法

