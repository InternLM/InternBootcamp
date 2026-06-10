import re
import json
from typing import Optional, Dict, Any
from internbootcamp.src.base_reward_calculator import BaseRewardCalculator

# 导入依赖库
import random
import re
from collections import defaultdict




class CrotationmatchingRewardCalculator(BaseRewardCalculator):
    """Crotationmatching奖励计算器"""
    
    @staticmethod
    def extract_output(output):
        matches = re.findall(r'\[answer\](.*?)\[/answer\]', output, re.DOTALL)
        if not matches:
            return None
        last_match = matches[-1].strip()
        try:
            return int(last_match)
        except ValueError:
            return None
    
    @classmethod
    def _verify_correction(cls, solution, identity):
        n = identity['n']
        a = identity['a']
        b = identity['b']
        
        if n == 0:
            return solution == 0
        
        p1 = {x: idx for idx, x in enumerate(a)}
        p2 = {x: idx for idx, x in enumerate(b)}
        delta_counts = defaultdict(int)
        
        for x in a:
            delta = (p1[x] - p2[x]) % n
            delta_counts[delta] += 1
        
        max_count = max(delta_counts.values()) if delta_counts else 0
        return solution == max_count
    
    # 其他额外方法

