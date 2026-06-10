import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re




class DqueueRewardCalculator(BaseRewardCalculator):
    """Dqueue奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_answer = matches[-1].strip()
        try:
            return int(last_answer)
        except (ValueError, TypeError):
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        ti = identity['ti']
        ti_sorted = sorted(ti)
        if not ti_sorted:
            return solution == 0
        s = ti_sorted[0]
        o = 1
        for x in range(len(ti_sorted) - 1):
            next_t = ti_sorted[x + 1]
            if s <= next_t:
                s += next_t
                o += 1
        return solution == o
    
    # 其他额外方法

